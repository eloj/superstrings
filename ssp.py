"""Approximate Shortest Superstrings

MIT License
Copyright (c) 2024 Eddy Jansson

See https://github.com/eloj/superstrings
"""

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
	for i, ai in enumerate(arr):
		ssf = True
		for j, aj in enumerate(arr):
			if i != j and ai in aj:
				ssf = False
				break
		if ssf:
			res.append(ai)

	return res

def find_max_overlap(s1: str, s2: str) -> tuple[int, str]:
	"""
	Find the maximum overlap and "merge" of two strings.

	Note that here f(s,s) => len(s), s

	Args:
		s1, s2: Strings to find overlap between.
	Returns:
		int, str: The length of the maximum overlap, and the merge string.
	"""
	len1 = len(s1)
	len2 = len(s2)

	# PERF: This handles cases where the input is not substring-free.
	# This is not a part of the standard formulation of GREEDY, but helps
	# in practice on input that has not been preprocessed to deal with this.
#	if s1 in s2:
#		return len1, s2
#	if s2 in s1:
#		return len2, s1

	max_i, max_j = 0, 0
	for i in range(1, min(len1, len2) + 1):
		# Try matching s1.suffix(i) with s2.prefix(i)
		if s1[len1-i:] == s2[:i]:
			max_i = i
		# Try matching s1.prefix(i) with s2.suffix(i)
		# PERF: if len1 == len2, the full words are redundantly checked a second time here.
		if s1[:i] == s2[len2-i:]:
			max_j = i

	if max_i >= max_j:
		return max_i, s1 + s2[max_i:]

	return max_j, s2 + s1[max_j:]

"""
Algorithm GREEDY:
	Start with the input set S.
	Pick two strings a,b with maximum overlap from S,
		combine them into one string called the 'merge',
		and insert that back into the set, replacing a and b.
	Once there is only one string in S, the algorithm terminates.

This is conjectured to be within a factor 2 of optimal.

References:
	"Linear Approximation of Shortest Superstrings", Blum et al., 1994.
	https://ir.cwi.nl/pub/1422/1422D.pdf
	"The greedy algorithm for shortest superstrings", Kaplan & Shafrir, 2004.
	https://doi.org/10.1016/j.ipl.2004.09.012

Notes:
	The overlap calculation is not strictly equal to the formulation in Blum,
		specifically w.r.t self-overlap.
	The quality of the solution generated can be sensitive to the order of the inputs.
"""
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
	n = len(arr)
	while n > 1:
		longest_overlap, l, r = 0, 0, 0
		merge = None

		for i in range(n):
			for j in range(i+1, n):
				overlap, s = find_max_overlap(arr[i], arr[j])
				if overlap > longest_overlap:
					longest_overlap = overlap
					l, r = i, j
					merge = s

		n -= 1

		if merge:
			# Replace one pair with the 'merge' (longest overlap), the other with the last candidate.
			arr[l] = merge
			arr[r] = arr[n]
		else:
			# No overlap, best we can do is concatenate. Last element is convenient. Is there a heuristic for this?
			arr[0] += arr[n]
		# arr.pop() # trim array -- not necessary with how we iterate
	# ... while n > 1

	return arr[0]


def generate_superstring(strings: list[str]) -> str:
	"""
	Generate an approximate Superstring.

	Args:
		strings: Input, e.g a set of words.
		method: Name of superstring function to use.
	Returns:
		str: An approximate superstring of the input.
	"""
	return greedy(make_substring_free(strings))


if __name__ == "__main__":
	# from random import shuffle

	# Hard input for GREEDY. Kaplan 2005.
	# { c(ab)^k, (ba)^k, (ab)^kc }
	# arr = ["cababab", "bababa", "abababc" ]
	# GREEDY=cabababcbababa, OPT=cababababc
	arr = ['n', 'ora', 'bne', 'eor']

	arr = make_substring_free(arr)
	print(arr)
	# shuffle(arr)

	res = generate_superstring(arr)
	print(f"{res}, len={len(res)}")
