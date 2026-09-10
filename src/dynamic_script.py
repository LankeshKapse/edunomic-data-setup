import argparse
import os
from typing import Any, Dict, List, Optional

from utils.payload_factory import PayloadFactory, get_address_dict
from utils.request_utility import RequestUtility
from utils.utilities import ConfigLoader

# The org hierarchy is a chain: each stage's id feeds into the next stage's
# payload as a foreign key. Add/remove/reorder stages here instead of writing
# a new block of code for each one.
# NOTE: disabling a stage here cascades -- every later stage that depends on
# it (directly or transitively, via parent_key) is skipped too. See
# run_pipeline() for the cascade logic.
ORG_PIPELINE: List[Dict[str, Any]] = [
    {
        "name": "trust",
        "uri": "/trust",
        "parent_key": None,  # root of the chain, no parent id to inject
        "include_address": True,
        "extract": ["trustId", "trustName"],
    },
    {
        "name": "university",
        "uri": "/university",
        "parent_key": "trustId",
        "include_address": True,
        "extract": ["universityId", "universityName"],
    },
    {
        "name": "school",
        "uri": "/school",
        "parent_key": "universityId",
        "include_address": True,
        "extract": ["schoolId", "schoolName"],
    },
    {
        "name": "program",
        "uri": "/program",
        "parent_key": "schoolId",
        "include_address": True,
        "drop_keys": ["city"],  # program payload doesn't want the address's city field
        "extract": ["programId", "programName"],
    },
]

# Master/reference data. Same shape as ORG_PIPELINE (list of dicts with a
# "name") so both configs can be loaded/parsed and run the same way. Every
# stage here has parent_key=None (no chaining), so "enabled" is always safe
# to toggle -- unlike ORG_PIPELINE, disabling one entry can't strand a later
# entry without a parent id.
MASTER_PIPELINE: List[Dict[str, Any]] = [
    {
        "name": "designation",
        "uri": "/designation",
        "extract": ["designationId", "designationName"],
        "enabled": True,
    },
    {
        "name": "role",
        "uri": "/roles",
        "extract": ["roleId", "roleName"],
        "enabled": False,
    },
    {
        "name": "quota",
        "uri": "/quota",
        "extract": ["quotaId", "quotaName"],
        "enabled": True,
    },
    {
        "name": "category",
        "uri": "/category",
        "extract": ["categoryId", "categoryName"],
        "enabled": True,
    },
    {
        "name": "document",
        "uri": "/document",
        "extract": ["documentId", "documentName"],
        "enabled": True,
    },
    {
        "name": "credit-framework",
        "uri": "/credit-framework",
        "extract": ["creditFrameworkId", "qualificationTitle"],
        "enabled": True,
    },
]

# Each entry is one full hierarchy chain, plus which host it targets and
# which "setup.config" section its PayloadFactory should be built from.
ALL_PIPELINES: Dict[str, Dict[str, Any]] = {
    "org": {"host_property": "app.outbound.org", "stages": ORG_PIPELINE},
    "master": {"host_property": "app.outbound.master", "stages": MASTER_PIPELINE},
    # ... more entries, or generate this dict from a config file
}


def build_payload(payload_factory: PayloadFactory,
                   config_name: str,
                   key_id: Optional[Any],
                   key_name: Optional[str],
                   include_address: bool = False,
                   drop_keys: Optional[List[str]] = None
                   ) -> Dict[str, Any]:
    payload: Dict[str, Any] = payload_factory.build(config_name)

    if key_id is not None and key_name is not None:
        payload[key_name] = key_id

    if include_address:
        payload.update(get_address_dict())

    for key in drop_keys or []:
        payload.pop(key, None)

    return payload


def run_pipeline(request_utility: RequestUtility,
                  payload_factory: PayloadFactory,
                  host: str,
                  pipeline: List[Dict[str, Any]]
                  ) -> Dict[str, Dict[str, Any]]:
    """Create each entity in a pipeline, feeding each result forward as the
    parent id for the next stage (when parent_key is set). Returns every
    *created* entity keyed by stage name -- a disabled or skipped stage is
    simply absent from the returned dict, it is not present with a None
    value.

    Disabling cascades down the chain: if a stage is disabled (or itself
    got skipped because ITS parent was disabled), every later stage that
    depends on it via parent_key is skipped too, rather than being created
    with a missing/None foreign key. Stages with parent_key=None (e.g. every
    entry in MASTER_PIPELINE, or a stage that starts a new independent
    branch) are never affected by this -- they only skip when explicitly
    disabled.
    """
    parent_entity: Dict[str, Any] = {}
    created: Dict[str, Dict[str, Any]] = {}
    chain_broken = False

    for stage in pipeline:
        parent_key = stage.get("parent_key")

        if not stage.get("enabled", True):
            chain_broken = True
            continue

        if parent_key and chain_broken:
            # An earlier stage this one depends on was skipped -- skip this
            # one too, and leave chain_broken set so anything further down
            # the same chain keeps skipping.
            continue

        key_id = parent_entity.get(parent_key) if parent_key else None

        payload = build_payload(
            payload_factory=payload_factory,
            config_name=stage["name"],
            key_id=key_id,
            key_name=parent_key,
            include_address=stage.get("include_address", False),
            drop_keys=stage.get("drop_keys"),
        )

        entity = request_utility.create_entity(host, stage["uri"], payload, stage["extract"])
        created[stage["name"]] = entity
        parent_entity = entity

    return created


def run_all_pipelines(request_utility: RequestUtility,
                       prop: ConfigLoader,
                       pipelines: Dict[str, Dict[str, Any]]
                       ) -> Dict[str, Dict[str, Dict[str, Any]]]:
    results: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for name, cfg in pipelines.items():
        host = prop.get_property(cfg["host_property"])
        setup_config = prop.get_list("setup.config", name)
        payload_factory = PayloadFactory(setup_config)
        results[name] = run_pipeline(request_utility, payload_factory, host, cfg["stages"])
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Org and master data setup")
    parser.add_argument(
        "--env",
        default=os.environ.get("APP_ENV", "dev"),
        help="Environment name; resolves to ../config/application-<env>.yml",
    )
    args = parser.parse_args()

    apps_yml_path: str = f"../config/application-{args.env}.yml"

    request_utility: RequestUtility = RequestUtility()
    prop: ConfigLoader = ConfigLoader(path=apps_yml_path)

    run_all_pipelines(request_utility, prop, ALL_PIPELINES)


if __name__ == "__main__":
    main()