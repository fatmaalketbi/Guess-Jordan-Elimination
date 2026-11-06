#%%
from fractions import Fraction
from copy import deepcopy


def F(value):
    """Convert an integer, string, or Fraction to an exact Fraction."""
    return value if isinstance(value, Fraction) else Fraction(value)


def as_fraction_matrix(matrix):
    """Return a deep copy of matrix with every entry stored as a Fraction."""
    if not matrix or not matrix[0]:
        raise ValueError("The matrix must be non-empty.")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("All rows must have the same number of entries.")
    return [[F(entry) for entry in row] for row in matrix]


def show_matrix(matrix):
    """Print a matrix in a compact, readable form."""
    for row in matrix:
        print("[ " + "  ".join(f"{str(x):>7}" for x in row) + " ]")
    print()

#%%
def swap_rows(M, i, j):
    A = deepcopy(M)
    A[i], A[j] = A[j], A[i]
    return A


def scale_row(M, i, k):
    k = F(k)
    if k == 0:
        raise ValueError("k can not be zero")
    A = deepcopy(M)
    A[i] = [k * x for x in A[i]]
    return A

def replace_row(M, i, j, k):
    if i == j:
        raise ValueError("i and j must be different")
    k = F(k)
    A = deepcopy(M)
    A[i] = [
        A[i][col] + k * A[j][col]
        for col in range(len(A[i]))
    ]
    return A
#%%
# Quick checks for Part 1
M0 = as_fraction_matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
assert swap_rows(M0, 0, 2) == as_fraction_matrix([[7, 8, 9], [4, 5, 6], [1, 2, 3]])
assert scale_row(M0, 1, Fraction(1, 2))[1] == [2, Fraction(5, 2), 3]
assert replace_row(M0, 2, 0, -7)[2] == [0, -6, -12]
print("Part 1 checks passed.")

#%%
def gauss_jordan(augmented, show_steps=False):
    M = as_fraction_matrix(augmented)
    operations = []
    pivot_row = 0
    coefficient_columns = len(M[0]) - 1

    for col in range(coefficient_columns):
        nonzero_row = None #finds a non zero entry
        for r in range(pivot_row, len(M)):
            if M[r][col] != 0:
                nonzero_row = r
                break

        # here if the  column below the pivot is zero it moves to next column
        if nonzero_row is None:
            continue

        # here it will swap the rows if it is needed
        if nonzero_row != pivot_row:
            M = swap_rows(M, pivot_row, nonzero_row)

            operations.append(
                f"R{pivot_row + 1} <-> R{nonzero_row + 1}"
            )

            if show_steps:
                print(operations[-1])
                show_matrix(M)

        # this will scale the pivot row so that the pivot becomes 1
        pivot = M[pivot_row][col]
        if pivot != 1:
            factor = Fraction(1, 1) / pivot
            M = scale_row(M, pivot_row, factor)

            operations.append(
                f"R{pivot_row + 1} -> ({factor})R{pivot_row + 1}"
            )

            if show_steps:
                print(operations[-1])
                show_matrix(M)

        # this s makes all other entries in this pivot column zeros
        for r in range(len(M)):
            if r != pivot_row and M[r][col] != 0:
                factor = -M[r][col]
                M = replace_row(M, r, pivot_row, factor)

                operations.append(
                    f"R{r + 1} -> R{r + 1} + ({factor})R{pivot_row + 1}"
                )
                if show_steps:
                    print(operations[-1])
                    show_matrix(M)
        # this moves down to the next pivot row
        pivot_row += 1

        # this will stop the function if there is no more rows
        if pivot_row == len(M):
            break

    return M, operations
#%%
# Lecture-style check: this system has the solution (-2, 2).
lecture_system = [[1, 2, 2], [3, 5, 4]]
lecture_rref, lecture_operations = gauss_jordan(lecture_system)
show_matrix(lecture_rref)
assert lecture_rref == as_fraction_matrix([[1, 0, -2], [0, 1, 2]])
print("Part 2 check passed.")

#%%
def nonzero_row_count(matrix):
    count = 0
    for row in matrix:
        if any(entry != 0 for entry in row):
            count += 1
    return count

def classify_system(rref_augmented):
    M = as_fraction_matrix(rref_augmented)
    number_of_variables = len(M[0]) - 1
    coefficient_matrix = [row[:-1] for row in M]

    rank_A = nonzero_row_count(coefficient_matrix)
    rank_augmented = nonzero_row_count(M)

    if rank_A != rank_augmented:
        classification = "no solution"
    elif rank_A == number_of_variables:
        classification = "unique solution"
    else:
        classification = "infinitely many solutions"
    return {
        "rank_A": rank_A,
        "rank_augmented": rank_augmented,
        "number_of_variables": number_of_variables,
        "classification": classification
    }
#%%
systems = {
    "System A": [
        [1, 2, -1, 3],
        [2, -1, 1, 2],
        [3, 1, 1, 7],
    ],
    "System B": [
        [1, 2, -1, 1, 3],
        [2, 4, -2, 2, 6],
        [0, 1, 1, -1, 1],
    ],
    "System C": [
        [1, -1, 2, 1],
        [2, -2, 4, 3],
        [0, 1, -1, 0],
    ],
}
#%%
# TODO: analyze System A, System B, and System C.
for name, augmented in systems.items():
    print(name)
    print("Original augmented matrix:")
    show_matrix(as_fraction_matrix(augmented))

    rref, operations = gauss_jordan(augmented)

    print("Row operations:")
    for operation in operations:
        print(operation)

    print("\nRREF:")
    show_matrix(rref)

    info = classify_system(rref)

    print("Rank(A):", info["rank_A"])
    print("Rank([A|b]):", info["rank_augmented"])
    print("Classification:", info["classification"])

    if info["classification"] == "unique solution":
        solution = [row[-1] for row in rref]
        print("Solution:", solution)

    elif info["classification"] == "infinitely many solutions":
        parameters = info["number_of_variables"] - info["rank_A"]
        print("Number of parameters:", parameters)

    elif info["classification"] == "no solution":
        for row_number, row in enumerate(rref, start=1):
            if all(x == 0 for x in row[:-1]) and row[-1] != 0:
                print("Impossible equation is in row", row_number, ":", row)

    print("-" * 40)

#%%
A_homogeneous = [
    [1, 2, -1, 3],
    [2, 4, -2, 6],
    [0, 1, 1, -1],
]

# TODO: append the zero column, analyze the system, and give the answer.
# Add the zero constant column
augmented_homogeneous = [row + [0] for row in A_homogeneous]
print("original augmented matrix :")
show_matrix(as_fraction_matrix(augmented_homogeneous))
# here it finds reduced row echlon form
rref, operations = gauss_jordan(augmented_homogeneous)
print("Row operations:")
for operation in operations:
    print(operation)
print("\nRREF:")
show_matrix(rref)
# this will classify the linear system
info = classify_system(rref)
rank_A = info["rank_A"]
number_of_variables = info["number_of_variables"]
parameters = number_of_variables - rank_A

print("Rank(A):", rank_A)
print("Number of parameters:", parameters)

if parameters > 0:
    print("Nonzero solutions exist: Yes")
else:
    print("Nonzero solutions exist: No")

print("Vector form:")
print("x = s(3, -1, 1, 0) + t(-5, 1, 0, 1)")

#%%
mysystem = [
    [0, 1, 1, 2],
    [1, 1, 0, 3],
    [2, -1, 1, 1]
]

print("My test system:")
show_matrix(as_fraction_matrix(mysystem))
rref, operations = gauss_jordan(mysystem)

print("Row operations:")
for operation in operations:
    print(operation)

print("\nRREF:")
show_matrix(rref)

info = classify_system(rref)
print(info)