#!/usr/bin/env python3
#
# See https://github.com/eloj/superstrings/
#
from math import log, log2, ceil
import random
import ssp
import sys

# *WARNING* -- this tool is a total hack, and some of the options/output is only half-working, interacts in odd ways, or
# maybe even fully broken. Caveat emptor!

# TODO: add args parsing -- https://docs.python.org/3/howto/argparse.html
# TODO: remove 'joined' stuff, this should be possible via args.
# TODO: correctly handle indeces vs offsets thoughtout, with option
# TODO: generate illegal-mask bytes array (make sure C64-decode is viable)
# TODO: --shuffle argument vs --sort for the input
# TODO: fix file loading relying on case to encode 'illegal'.. take as arg.
# TODO: --transform funcname,funcname ... chained, transform_input_binary should take words size (in bits).
# TODO: ?? min/max klen should be in bits?
# TODO: bitmap(s) to denote word starts, endings.

def bits(n):
	if n == 0:
		return 1
	return ceil(log2(n))

def find_aligned(haystack, needle):
	klen = len(needle)
	for i in range(0, len(haystack)-1, klen):
		if haystack[i:i+klen] == needle:
			return i
	return -1

def shannon_entropy(s):
	pdist = [s.count(c) / len(s) for c in set(s)]
	# print("Symbol probability distribution: ", pdist)
	return -sum([p*log(p) / log(2.0) for p in pdist])

def transform_input_5bit(s, encode=True):
	res = ""
	if encode:
		for c in s:
			res += "x{0:05b}".format(ord(c)-65)
	else:
		for i in range(1, len(s), 5+1):
			res += s[i:i+5]
	return res

def transform_input_binary(s, encode=True):
	if not encode:
		return s
	res = ""
	for c in s:
		res += "{0:05b}".format(ord(c)-65)
	return res

if __name__ == "__main__":
	dosuperstring = True
	# Best  with   undocumented: True, False
	# Best without undocumented: False, True
	dosort = False
	jamswap = False
	dotransform = False
	doreverse = False
	doshuffle = False

	use_indeces = False
	forcelengths = False
	symbits = 8
	lines = []
	arr = []
	before_len = 0
	before_unique_len = 0
	min_klen = 2**16
	max_klen = 0

	name_offsets = "offsets"

	if len(sys.argv) == 1:
		filename = "data/MOS6510-mnem-basic.txt"
	else:
		filename = sys.argv[1]

	if doreverse:
		print("Reversing each input element")
	if dotransform:
		print("Transforming each input element")

	with open(filename, 'r', encoding="utf-8") as fp:
		lines = fp.readlines()
	for v in lines:
		if v.startswith("#"):
			continue
		new_v = v.strip()
		if doreverse:
			new_v = "".join(reversed(new_v))
		if dotransform:
			new_v = transform_input_5bit(new_v)
		if len(new_v) < min_klen:
			min_klen = len(new_v)
		if len(new_v) > max_klen:
			max_klen = len(new_v)
		before_len += len(new_v)
		arr.append(new_v)

	dolengths = forcelengths or min_klen != max_klen

	# Make a copy of the original input, must be used to calculate the offsets later.
	mnem = arr.copy()

	if dosort:
		print("Sorting input by frequency")
		hist = {}
		for i, v in enumerate(arr):
			if v in hist:
				hist[v] += 1
			else:
				hist[v] = 1
		arr = sorted(hist, key=hist.get, reverse=True)
		#print("Histogram:")
		#for k in arr:
		#	print(f"{k} => {hist[k]}")
	else:
		print("Removing duplicate entries from input")
		arr = [i for n, i in enumerate(arr) if i not in arr[:n]]

	if doshuffle:
		print("Shuffling input")
		random.shuffle(arr)

	if jamswap:
		for i, v in enumerate(arr):
			if v == "JAM":
				if i == 0:
					break
				arr[0], arr[i] = arr[i], arr[0]
				print(f"Swapped JAM at index {i}")
				break

	for v in arr:
		before_unique_len += len(v)

	print(f"{len(mnem)} strings (total len={before_len}, min/max len={min_klen}/{max_klen}) in input, {len(arr)} unique strings (total len={before_unique_len}) remain.")

	print(arr)

	res = ""
	if dosuperstring:
		# work_arr = arr.copy()
		res = ssp.generate_superstring(arr)
		# XXX: HACK
		res_noalign = res.replace("x", "")
		opt_len = len(res_noalign)
		saved = before_len - opt_len
		saved_unique = before_unique_len - opt_len
		print(f"Generated Superstring is {opt_len} characters, saving {saved}/{saved_unique}:\n{res_noalign}")
	else:
		use_indeces = min_klen == max_klen # and not force_offsets
		if use_indeces:
			name_offsets = "indeces"
		res = "".join(arr)
		# XXX: HACK
		res_noalign = res.replace("x", "")
		print(f"Joined string is {len(res_noalign)} characters (use_indeces={use_indeces}):\n{res_noalign}")

	# NOTE: only valid for character strings (not binary strings). TODO to fix.
	shannonh = shannon_entropy(res_noalign)
	print("Shannon entropy(s): {:.6f} bits/symbol, {:.4f} bits ({} bytes)".
		format(shannonh, shannonh*len(res_noalign), ceil(shannonh*len(res_noalign)/8.0)))

	alphabet = "".join(sorted(set(res_noalign)))
	alphabet_size = len(alphabet)
	symbol_size_bits = bits(alphabet_size)
	print(f"Alphabet size={alphabet_size} ({symbol_size_bits} bits/symbol):\n{alphabet}")

	offsets = []
	lengths = []
	total_index_bits_estimate = 0
	for v in mnem:
		ofs = res.index(v)
		if use_indeces:
			ofs = find_aligned(res, v)
			if ofs == -1 or ofs % min_klen != 0:
				print(f"ERROR: Found offset {ofs} isn't multiple of {min_klen} as required in indeces mode.")
				exit(1)
			ofs = ofs // min_klen
		b = bits(ofs)
		total_index_bits_estimate += b

		# TODO: if all keys same length, use index instead of offset.
		offsets.append(ofs)
		lengths.append(len(v))

		# Verification step:
		if use_indeces:
			ofs = ofs * min_klen
		if v != res[ofs:ofs+len(v)]:
			print("ERROR in encoding! You've done goofed up!")
			print(f"Expected {v} at offset {ofs}, got {res[ofs:ofs+len(v)]}")
			exit(1)

	if symbits != 8: # TODO: this is not really the right conditional
		print("Superstring table in hex:")
		# Iterate over octets
		for i in range(0, len(res_noalign), 8):
			sym = res_noalign[i:i+8].ljust(8, "0")
			print("{0:02x}, ".format(int(sym,2)), end="")
		print("")
		if not use_indeces:
			offsets = [x // (symbits+1) for x in offsets] ## HACK

	# We allow encoding zero-lengths for simplicity, but a general min_klen -offset could be used.
	max_index = max(offsets)
	max_index_bits = bits(max_index)
	index_length_max = 0
	index_size_max = max_index_bits * len(offsets) // 8
	print(f"The {len(offsets)} verified ok {name_offsets} (~{total_index_bits_estimate}/{index_size_max}*8 bits, min unit={max_index_bits} bits) are:")
	print(offsets)
	print("min/max offset={}/{}".format(min(offsets), max_index))
	# TODO: if klen uniform, then last offset must be length of superstring - klen

	if dolengths:
		max_length_bits = bits(max_klen)
		index_length_max = max_length_bits * len(lengths) // 8
		# opt_lengths = [v - min_klen for v in lengths]
		print(f"The {len(lengths)} lengths for kmin/kmax={min_klen}/{max_klen}, min unit={max_length_bits} bits, ({index_length_max} bytes total) are:")
		if max_length_bits > bits(max_klen - min_klen):
			print("NOTE: Could be optimized by subtracting out kmin first, for smaller min unit.")
		print(lengths)

	# TODO: opt_len should be 'res_octet_len'
	if dosuperstring:
		print(f"Superstring: {opt_len} + {index_size_max} + {index_length_max} = {opt_len + index_size_max + index_length_max} bytes.")
	print(f"Direct: {before_len} bytes.")

