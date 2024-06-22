#!/usr/bin/env python3
#
# Approximate Shortest Superstring Generator
# https://github.com/eloj/superstrings/
#
# Copyright © 2024 Eddy Jansson
# Licensed under the MIT License. See LICENSE file for details.
#
from math import log2, ceil
import argparse
import random
import ssp
import sys

# TODO: bits/bytes helper print function
# TODO: transforms: (test with emoji!)
# TODO: --bps --bits-per-symbol [auto,1-32] (default=8)
# TODO: --to-bitstrings
# TODO: ?? --from-bitstrings (i.e input already bitstrings, adapt bps etc)
#
# TODO: correctly handle indeces vs offsets thoughtout, with option
# TODO: ?? min/max klen should be in bits?
# TODO: bitmap(s) to denote word starts, endings, iff variable klen.

PROGRAM_VERSION = "1.0.0"

def bits(n):
	if n == 0:
		return 1
	return ceil(log2(n))

def calculate_bits_per_character(string, char_base='A'):
	a = 0
	for ch in string:
		a |= ord(ch) - ord(char_base)
	# print(a, bin(a))
	return bits(a)

def data_loader(args):
	res = []

	with open(args.infile, 'r', encoding="utf-8") as fp:
		lines = fp.readlines()

	for v in lines:
		is_comment = False
		for prefix in args.comment:
			if len(prefix) > 0 and v.startswith(prefix):
				is_comment = True
				break
		if is_comment:
			continue

		res.append(v.strip())

	return res

def apply_move_to_front(arr, args):
	for k in args.mtf:
		idx = arr.index(k)
		if idx > 0:
			arr.insert(0, arr.pop(idx))
			if not args.quiet:
				print(f"Moved {arr[0]} at index {idx} to front.")
	return

if __name__ == "__main__":
	argp = argparse.ArgumentParser()

	vgroup = argp.add_mutually_exclusive_group()
	vgroup.add_argument("-q", "--quiet", help="Only output generated string", action="store_true")
	vgroup.add_argument("-v", "--verbose", help="Increase output verbosity", action="count", default=0)

	order_group = argp.add_mutually_exclusive_group()
	order_group.add_argument("-s", "--shuffle", help="Shuffle the input", action="store_true", default=False)
	order_group.add_argument("-S", "--sort", help="Sort input by frequency of terms", action="store_true", default=False)

	argp.add_argument("--comment", help="String(s) that start a comment in the input", action="extend", nargs=1, type=str)
	argp.add_argument("--mtf", help="Input element(s) to move-to-front", action="extend", nargs=1, type=str)
	argp.add_argument("-J", "--join-only", help="Only join input, don't generate superstring", action="store_true")
	# argp.add_argument("--bps", help="Encode as n bits-per-symbol", action="extend", type=int, default=8)
	argp.add_argument("-I", "--index-table", help="Always output offset/index table", action="store_true")
	argp.add_argument("-L", "--length-table", help="Always output lengths table", action="store_true")
	argp.add_argument("--rebase-lengths", help="Rebased lengths based on kmin", action="store_true")

	argp.add_argument("-V", "--version", help="Display program version and exit", action="version", version=PROGRAM_VERSION)
	argp.add_argument("infile", help="Input set of strings, one per line")

	args = argp.parse_args()

	# https://github.com/python/cpython/issues/60603
	if args.comment == None:
		args.comment = ['#']
	if args.verbose > 1:
		print(f"Comment prefix(es): {args.comment}")

	original_input = data_loader(args)
	input_bps = 0
	transformed_input = []

	min_klen = 2**16
	max_klen = 0
	original_input_len = 0
	unique_input_len = 0

	for v in original_input:
		klen = len(v)
		if klen < min_klen:
			min_klen = klen
		if klen > max_klen:
			max_klen = klen
		original_input_len += klen

	print_length_table = args.length_table or min_klen != max_klen

	if args.sort:
		if not args.quiet:
			print("Removing duplicates by sorting input by frequency.")
		hist = {}
		for i, v in enumerate(original_input):
			if v in hist:
				hist[v] += 1
			else:
				hist[v] = 1
		unique_input = sorted(hist, key=hist.get, reverse=True)
		if args.verbose > 1:
			print("Histogram:")
			for k in unique_input:
				print(f"{k} => {hist[k]}")
	else:
		if not args.quiet:
			print("Removing duplicates from input.")
		unique_input = [i for n, i in enumerate(original_input) if i not in original_input[:n]]

	if args.shuffle:
		if not args.quiet:
			print("Shuffling input.")
		random.shuffle(unique_input)

	if args.mtf is not None:
		if args.verbose > 0:
			print(f"Applying move to front on input set {args.mtf}")
		apply_move_to_front(unique_input, args)

	for v in unique_input:
		unique_input_len += len(v)

	# Calculate fixed bits-per-symbol from input.
	## if input_bps == 0:
	## 	input_alphabet = "".join(sorted(set("".join(unique_input))))
	## 	input_bps = calculate_bits_per_character(input_alphabet, input_alphabet[0])
	## 	if not args.quiet:
	## 		print(f"Auto-detected bits-per-symbol of input: {input_bps}")

	#
	# TODO: transformations: n-bit re-encode + bitstring support
	#
	transformed_input = unique_input

	#
	# Output stats on input data set
	#
	if args.verbose:
		print(f"{len(original_input)} strings (total len={original_input_len}, min/max klen={min_klen}/{max_klen}) in input, {len(unique_input)} unique strings (total len={unique_input_len}) remain.")
	if not args.quiet:
		if args.verbose:
			print("Final pre-processed input:")
		print(transformed_input)

	output = None
	if args.join_only:
		output = "".join(transformed_input)
	else:
		output = ssp.generate_superstring(transformed_input)

	#
	# Calculate and verify offsets
	#
	offsets = []
	lengths = []
	total_index_bits_estimate = 0
	for v in original_input:
		ofs = output.index(v)
		b = bits(ofs)
		total_index_bits_estimate += b

		offsets.append(ofs)
		lengths.append(len(v))

		# Verification step:
		if v != output[ofs:ofs+len(v)]:
			print("ERROR in encoding! You've done goofed up!")
			print(f"Expected {v} at offset {ofs}, got {res[ofs:ofs+len(v)]}")
			exit(1)

	#
	# Output alphabet and alphabet size
	#
	if args.verbose > 0:
		output_alphabet = "".join(sorted(set(output)))
		print(f"Output alphabet size={len(output_alphabet)}:\n{output_alphabet}")

	#
	# Output superstring
	#
	if not args.quiet:
		opt_len = len(output)
		saved = original_input_len - opt_len
		saved_unique = unique_input_len - opt_len
		print(f"Generated Superstring is {opt_len} characters, saving {saved} on original, {saved_unique} on unique:")
	print(output)

	#
	# Output index table
	#
	if args.index_table:
		if not args.quiet:
			max_index = max(offsets)
			max_index_bits = bits(max_index)
			index_size_max = max_index_bits * len(offsets) // 8
			print(f"The {len(offsets)} verified ok offsets (~{total_index_bits_estimate}/{index_size_max}*8 bits, min unit={max_index_bits} bits) are:")
		print(offsets)

	#
	# Output length table
	#
	if print_length_table:
		max_length_bits = bits(max_klen)

		if args.rebase_lengths:
			lengths = [a - min_klen for a in lengths]
			max_length_bits = bits(max_klen - min_klen)

		if not args.quiet:
			index_length_max = max_length_bits * len(lengths) // 8
			print(f"The {len(lengths)} lengths with min/max={min_klen}/{max_klen}, req. bits/entry={max_length_bits} bits, ({index_length_max} bytes total) are:")
			if max_length_bits > bits(max_klen - min_klen):
				print("NOTE: Could be optimized by subtracting out minimum first, for smaller unit size, see --rebase-lengths")
			if args.rebase_lengths:
				print(f"(lengths rebased, add back {min_klen} for true values)")
		print(lengths)
