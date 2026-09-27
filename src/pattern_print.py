
print("Print the square pattern")
n=5
for i in range(5):
    for j in range(n):
        print("#", end=" ")
    print()

print("---"*10)
print("Print the increasing pattern")
n=5
for i in range(5):
    for j in range(i+1):
        print("#", end=" ")
    print()

print("---"*10)
print("Print the decreasing pattern")
n=5
for i in range(5):
    for j in range(i,n):
        print("#", end=" ")
    print()

print("---"*10)
print("Print right sided tringle")
n=5
for i in range(5):

    for j in range(i,n):
        print(" ", end="")

    for k in range(i+1):
        print("*", end="")

    print()

print("---"*10)
print("Print left sided tringle")
n=5
for i in range(n):

    for j in range(i,n):
        print(" ", end="")

    for k in range(i+1):
        print("* ", end="")


    print()