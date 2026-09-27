import numpy as np

def reshape_array(arr: np.ndarray, shape: tuple) -> np.ndarray:
    """
    Reshape a NumPy array into the given shape.

    Note
    ----
    Reshaping only works if the total number of elements stays the same.
    That is, the product of the dimensions in `shape` must exactly equal
    the total number of elements in `arr` (i.e. `arr.size`).

        arr.size == shape[0] * shape[1] * ... * shape[n]

    Example
    -------
    An array of length 12 can be reshaped into:
        (3, 4)   -> 3 * 4 = 12   OK
        (2, 6)   -> 2 * 6 = 12   OK
        (4, 4)   -> 4 * 4 = 16   FAILS (size mismatch)

    Raises
    ------
    ValueError
        If the product of `shape` does not match `arr.size`.

    Parameters
    ----------
    arr : np.ndarray
        The input array to reshape.
    shape : tuple
        The target shape. You can use -1 for one dimension to let
        NumPy infer it automatically from the array's size.

    Returns
    -------
    np.ndarray
        The reshaped array (a view, when possible).
    """
    return arr.reshape(shape)

def expand_dims_demo(arr: np.ndarray, axis: int) -> np.ndarray:
    """
    Insert a new axis (dimension of size 1) into an array at the given position,
    without changing the underlying data.

    Note
    ----
    - `axis=0` adds a new dimension BEFORE the existing one.
      A 1D array of shape (3,) becomes shape (1, 3)  -> a "row vector".
    - `axis=1` adds a new dimension AFTER the existing one.
      A 1D array of shape (3,) becomes shape (3, 1)  -> a "column vector".
    - Equivalent to using `arr[np.newaxis, :]` (axis=0) or
      `arr[:, np.newaxis]` (axis=1), but more explicit/readable.

    Example
    -------
    arr = np.arange(3)                  # shape (3,)  -> [0, 1, 2]
    np.expand_dims(arr, axis=0)         # shape (1,3) -> [[0, 1, 2]]
    np.expand_dims(arr, axis=1)         # shape (3,1) -> [[0], [1], [2]]

    Real-life uses
    --------------
    1. Broadcasting fixes: reshape a 1D array to (N,1) or (1,N) so it
       aligns correctly with a 2D array during arithmetic operations.
    2. ML models: add a "batch dimension" so a single sample
       (H, W, C) becomes (1, H, W, C) as expected by frameworks like
       TensorFlow/PyTorch/Keras.
    3. Row vs column vectors: control orientation for matrix
       multiplication (@) where (3,), (1,3), and (3,1) behave differently.
    4. Stacking along a new axis: expand multiple 1D arrays before
       np.concatenate to combine them into a 2D array.

    Parameters
    ----------
    arr : np.ndarray
        The input array to expand.
    axis : int
        Position at which the new axis is inserted.

    Returns
    -------
    np.ndarray
        A new view of `arr` with an additional dimension of size 1.
    """
    return np.expand_dims(arr, axis=axis)

def numpy_slice_view_demo(arr: np.ndarray) -> np.ndarray:
    """
    Demonstrate that NumPy array slicing returns a VIEW, not a copy —
    unlike native Python list slicing, which always returns a copy.

    Note
    ----
    - A NumPy slice shares the same underlying memory buffer as the
      original array. Modifying the slice modifies the original array,
      and vice versa.
    - A Python list slice creates a brand new list with copied elements.
      Modifying the slice has NO effect on the original list.
    - To force a NumPy slice to be an independent copy, use `.copy()`
      explicitly, e.g. `arr[1:3].copy()`.

    Example
    -------
    NumPy (view behavior):
        arr = np.array([1, 2, 3, 4, 5])
        sl = arr[1:3]        # sl = [2, 3], a VIEW into arr
        sl[0] = 99
        print(arr)           # [1, 99, 3, 4, 5]  <- original changed!

    Python list (copy behavior):
        lst = [1, 2, 3, 4, 5]
        sl = lst[1:3]        # sl = [2, 3], a separate COPY
        sl[0] = 99
        print(lst)           # [1, 2, 3, 4, 5]   <- original unchanged

    Forcing a copy in NumPy:
        arr = np.array([1, 2, 3, 4, 5])
        sl = arr[1:3].copy()  # independent copy
        sl[0] = 99
        print(arr)             # [1, 2, 3, 4, 5]  <- original unchanged

    Why this matters
    ----------------
    Relying on slice-is-a-copy behavior (as in plain Python) can
    introduce subtle bugs in NumPy code — an "innocent" slice + mutation
    can silently corrupt data elsewhere that still references the
    original array. Always use `.copy()` when you need true isolation.

    Parameters
    ----------
    arr : np.ndarray
        The input array to slice and demonstrate view behavior on.

    Returns
    -------
    np.ndarray
        A slice (view) of the original array.
    """
    return arr[1:3]

def broadcasting_demo(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Demonstrate NumPy broadcasting rules for combining arrays of
    different shapes without explicitly copying data.

    Rule
    ----
    Compare shapes from the RIGHT (trailing dimensions). Two dimensions
    are compatible if they are equal OR one of them is 1. Missing
    dimensions are padded with size 1 on the LEFT.

    Caveats
    -------
    1. A 1D array of shape (N,) is always padded to (1, N), never
       (N, 1). To broadcast down columns, reshape explicitly:
           col = arr.reshape(-1, 1)   # or arr[:, np.newaxis]
    2. Broadcasting creates a VIEW via strides, not a copy — memory
       efficient, but np.broadcast_to() results are READ-ONLY.
    3. Mismatched non-1 dimensions raise:
           ValueError: operands could not be broadcast together
    4. DANGEROUS: broadcasting can succeed with the WRONG axis
       alignment and produce silently incorrect results (e.g. adding
       a per-row bias that actually broadcasts per-column). Always
       verify which axis your 1D array is meant to align with.

    Example
    -------
    matrix = np.array([[1, 2, 3], [4, 5, 6]])   # shape (2, 3)
    row    = np.array([10, 20, 30])             # shape (3,)
    col    = np.array([100, 200]).reshape(2, 1) # shape (2, 1)

    matrix + row   # row broadcasts across each row      -> shape (2, 3)
    matrix + col   # col broadcasts down each column      -> shape (2, 3)

    Parameters
    ----------
    a : np.ndarray
        First input array.
    b : np.ndarray
        Second input array; broadcast against `a` per NumPy's rules.

    Returns
    -------
    np.ndarray
        Result of element-wise addition after broadcasting.

    Raises
    ------
    ValueError
        If `a` and `b` have incompatible shapes (no dimension pair is
        equal or 1, after right-alignment).
    """
    return a + b


def main():
    # Create np array
    print("Create np array")
    vector: np.ndarray = np.array(list(range(10)))
    print(vector)

    # Create np matrix
    print("Create np matrix")
    matrix: np.ndarray = np.array(
        [
            list(range(5)),
            list(range(5, 10))
        ]
    )
    print(matrix)

    # Vector from 0 to 9
    vector: np.ndarray = np.arange(10)
    print("Vector from 0 to 9")
    print(vector)

    # Matrix with two rows: [0..4] and [5..9]
    matrix: np.ndarray = np.vstack([np.arange(5), np.arange(5, 10)])
    print("Matrix with two rows: [0..4] and [5..9]")
    print(matrix)

    #implicit conversion
    print("implicit conversion".title())
    vector: np.ndarray = np.array([1,2,3,4,5,"X"])
    print(vector)

    # concatenating array
    print("concatenating array")
    arr1 : np.ndarray = np.linspace(1, 5,5, dtype=np.int16)
    arr2 : np.ndarray = np.linspace(6, 10,5, dtype=np.int16)
    arr3: np.ndarray = np.concatenate((arr1, arr2))
    print(arr3)

    print(f"{arr3.size=}")
    print(f"{arr3.dtype=}")
    print(f"{arr3.ndim=}")
    print(f"{len(arr3)=}")
    print(f"{arr3.shape=}")

    # Reshape array
    arr = np.arange(1,11)
    print(f"{arr=}")
    arr2 = arr.reshape(2,5)
    print(f"{arr2=}")

    # expand dimension
    print("expand dimension")
    arr:np.ndarray = np.arange(3)
    print(f"{arr=}")
    print(f"{arr.shape=}")
    expanded_axis0 = np.expand_dims(arr,axis=0)
    expanded_axis1 = np.expand_dims(arr,axis=1)
    print(f"{expanded_axis0=}")
    print(f"{expanded_axis0.shape=}")
    print(f"{expanded_axis1=}")
    print(f"{expanded_axis1.shape=}")

    # slicing operation
    print("slicing operation")
    arr: np.ndarray = np.arange(10)
    print(f"{arr=}")
    print(f"{arr[0]=}")
    print(f"{arr[-1]=}")
    print(f"{arr[3:5]=}")
    print(f"{arr[::2]=}")

    print("(3,2) array")
    arr: np.ndarray = np.array([
        [0,1],
        [2,3],
        [4,5],
    ])
    print(f"{arr=}")
    print(f"{arr[arr % 2 == 0]=}")
    print(f"{arr[arr % 2 != 0]=}")
    print(f"{arr[arr > 3]=}")

    print("multiple condition")
    arr: np.ndarray = np.arange(20)
    print(f"{arr=}")
    print(f"{arr[(arr > 10) & (arr % 2 ==0)]=}")
    print(f"{(arr > 10) & (arr % 2 ==0)=}")

    print("Element wise changes")
    first: np.ndarray = np.array([1, 2, 3])
    second: np.ndarray = np.array([4, 5, 6])
    print(f"{first=}")
    print(f"{second=}")
    print(f"{first + second =}")
    print(f"{first - second =}")
    print(f"{first * second =}")
    print(f"{first / second =}")
    print(f"{first ** second =}")
    print(f"{first ** second =}")

    print("Matrix operation")
    matrix: np.ndarray = np.array([
        [1, 2],
        [3, 4]
    ])

    print(f"{matrix=}")
    print(f"{np.sum(matrix)=}")
    print(f"{np.sum(matrix, axis=0)=}")
    print(f"{np.sum(matrix, axis=1)=}")
    print(f"{np.prod(matrix)=}")
    print(f"{np.prod(matrix, axis=0)=}")
    print(f"{np.prod(matrix, axis=1)=}")

    print("Broadcasting...")




if __name__== "__main__":
    main()