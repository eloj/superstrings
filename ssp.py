"""Approximate Shortest Superstrings

MIT License
Copyright (c) 2024 Eddy Jansson

See https://github.com/eloj/superstrings
"""
from itertools import permutations # Used by brute()

def make_substring_free(arr: list[str]) -> list[str]:
    """
    Create a new list from the input that is substring free.

    Elements keep their relative order.

    Args:
        arr: Input, e.g a set of words.
    Returns:
        list[str]: A new list where no element is a substring of another.
    """
    res = []
    for i, arr_i in enumerate(arr):
        ssf = True
        for j, arr_j in enumerate(arr):
            if i != j and arr_i in arr_j:
                ssf = False
                break
        if ssf:
            res.append(arr_i)

    return res

def find_max_overlap(str1: str, str2: str) -> tuple[int, str]:
    """
    Find the maximum overlap and "merge" of two strings.

    Note that here f(s,s) => len(s), s, and if no overlap => 0, ""

    Args:
        str1, str2: Strings to find overlap between.
    Returns:
        int, str: The length of the maximum overlap, and the merge string.
    """
    len1 = len(str1)
    len2 = len(str2)

    # PERF: This handles cases where the input is not substring-free.
    # This is not a part of the standard formulation of GREEDY, but helps
    # in practice on input that has not been preprocessed to deal with this.
#   if str1 in str2:
#       return len1, str2
#   if str2 in str1:
#       return len2, str1

    # PERF: Canonically you'd only check suffix vs prefix (OR vice-versa),
    # PERF: but checking both ways generates slightly better superstrings _on average_.
    max_i, max_j = 0, 0
    for i in range(1, min(len1, len2) + 1):
        # Try matching str1.suffix(i) with str2.prefix(i)
        if str1[len1-i:] == str2[:i]:
            max_i = i
        # Try matching str1.prefix(i) with str2.suffix(i)
        # PERF: if len1 == len2, the full words are redundantly checked a second time here.
        if str1[:i] == str2[len2-i:]:
            max_j = i

    if max_i == 0 and max_j == 0:
        # No overlap. We don't care about the merge, don't waste time concatenating strings.
        return 0, ""

    if max_i >= max_j:
        return max_i, str1 + str2[max_i:]

    return max_j, str2 + str1[max_j:]

# Algorithm GREEDY:
#     Start with the input set S.
#     Pick two strings a,b with maximum overlap from S,
#         combine them into one string called the 'merge',
#         and insert that back into the set, replacing a and b.
#     Once there is only one string in S, the algorithm terminates.
#
# This is conjectured to be within a factor 2 of optimal.
#
# References:
#     "Linear Approximation of Shortest Superstrings", Blum et al., 1994.
#     https://ir.cwi.nl/pub/1422/1422D.pdf
#     "The greedy algorithm for shortest superstrings", Kaplan & Shafrir, 2004.
#     https://doi.org/10.1016/j.ipl.2004.09.012
#
# Notes:
#     The overlap calculation is not strictly equal to the formulation in Blum,
#         specifically w.r.t self-overlap.
#     The quality of the solution generated can be sensitive to the order of the inputs.
#
def greedy(arr: list[str]) -> str:
    """
    Generate an approximate Superstring using the Greedy Algorithm.

    For best performance the input should be substring-free, i.e
    contain no elements that are substrings of one another.
    A weaker constraint is no duplicates.

    Warning: The input array is modified in the process!

    Args:
        arr: Input, e.g a set of words.
    Returns:
        str: An approximate superstring of the input.
    """
    num = len(arr)
    while num > 1:
        longest_overlap, idx_i, idx_j = 0, 0, 0
        merge = None

        for i in range(num):
            for j in range(i+1, num):
                overlap, tmp_merge = find_max_overlap(arr[i], arr[j])
                if overlap > longest_overlap:
                    longest_overlap = overlap
                    idx_i, idx_j = i, j
                    merge = tmp_merge

        num -= 1

        if merge:
            # Replace one pair with the 'merge', the other with the last candidate.
            arr[idx_i] = merge
            arr[idx_j] = arr[num]
        else:
            # No overlap, best we can do is concatenate. Last element is convenient.
            # Is there a heuristic for this?
            arr[0] += arr[num]
        # arr.pop() # trim array -- not necessary with how we iterate
    # ... while n > 1

    return arr[0]

# Algorithm BRUTE
#
# For each ordering of the input, generate a superstring. Return the shortest one.
#
# Time: O(n-factorial)
#
# Notes:
#   Warning! Extremely slow. Can only be used on _very_ small inputs (N ~< 16).
#
# References:
#   "ADS1: Implementing SCS", Ben Langmead at https://www.youtube.com/watch?v=BHUgDbVC4js
#
def brute(arr: list[str]) -> str:
    """
    Generate Optimal Superstring using a brute-force enumeration.

    Args:
        arr: Input, e.g a set of words.
    Returns:
        str: The shortest common superstring of the input.
    """

    def overlap(a, b):
        start = 0
        while True:
            start = a.find(b[:1], start)
            if start == -1:
                return 0
            if b.startswith(a[start:]):
                return len(a) - start
            start += 1

    shortest = None
    for perm in permutations(arr):
        sup = perm[0]
        for i in range(len(arr) - 1):
            olen = overlap(perm[i], perm[i+1])
            sup += perm[i+1][olen:]
        if shortest is None or len(sup) < len(shortest):
            shortest = sup
    return shortest

def generate_superstring(strings: list[str], func=greedy) -> str:
    """
    Generate an approximate Superstring.

    Args:
        strings: Input, e.g a set of words.
        method: Name of superstring function to use.
    Returns:
        str: An approximate superstring of the input.
    """
    return func(make_substring_free(strings))


def basic_test():
    """ Basic functionality test """
    # Hard input for GREEDY. Kaplan 2005.
    # { c(ab)^k, (ba)^k, (ab)^kc }
    arr = ["cababab", "bababa", "abababc" ]
    # GREEDY=cabababcbababa, OPT=cababababc
    # arr = ['n', 'ora', 'bne', 'eor']

    arr = make_substring_free(arr)
    print(f"prefix-free input: {arr}")

    res = generate_superstring(arr)
    print(f"greedy(): {res}, len={len(res)}")

    res = generate_superstring(arr, brute)
    print(f"brute(): {res}, len={len(res)}")

if __name__ == "__main__":
    basic_test()
