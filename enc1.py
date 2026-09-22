#!/usr/bin/env python3
from math import ceil
from struct import unpack

# S = "JPNGNBFARMYSYCOGMBMUSAUSALBNICOMNERISLVATAIARGIBLZMBGRCYPHLCAFGNQATFLKAZECUBHSLBRBDIMNGABWAGOHTIGUYCZEHUNGINCXRGUMIPAKGUFROUGHAPRIDNKCOLTZAMMRMCODCMRSURYCHNCHLCHESLETHASYRGGYTLSOMYTKMLIESPMHLBVTUNBTNBRNPCNCPVGBRABOLCYMTQCIVENBLRGRDPRYJEYSXMNPLWLFSMOZGTMDVUTURBGDSSDNBESHNDGEOBELPERGRLSJMSRBHRVCTCDOMKDZAFRAPOLCUWSMLTUVIRNFKHMDAUTJKIRLSVNMAFJIRQJORPRTTONLDJIOTKLCRITATGOJAMEXSWZCOKNAMACCKENZLUXPRKORSGPSENCLBYSVKWTWNORWASMRTCANDEUKRBLMDGLPANIUZBIHKGZWEGYEMWISRBENRUSGSWESTPYFINDMAREUGALAO"
S = "BRKORAJAMASLPHPBPLCLCJSRANDBITROLPLPBMISECRTIEORLSRPHAJMPBVCCLIRTSADCRORPLABVSSEISTASTYSTXDEYTXABCCTYATXSLDYLDALDXTAYTAXBCSCLVTSXCPYCMPDECINYDEXBNECLDCPXSBCINCINXNOPBEQSED"
A = [87, 60, 90, 41, 483, 24, 424, 478, 43, 7, 418, 39, 65, 365, 21, 326, 70, 81, 275, 459, 266, 5, 259, 51, 289, 75, 443, 431, 225, 47, 17, 212, 209, 79, 199, 196, 191, 88, 59, 423, 384, 159, 156, 153, 220, 146, 143, 13, 377, 133, 29, 205, 361, 73, 309, 108, 215, 54, 99, 426, 354, 476, 130, 296, 300, 72, 450, 33, 267, 185, 468, 164, 473, 339, 67, 303, 120, 245, 86, 208, 272, 171, 124, 45, 105, 435, 15, 3, 62, 52, 228, 281, 250, 118, 111, 96, 445, 323, 269, 290, 93, 102, 129, 83, 474, 356, 331, 318, 341, 35, 456, 363, 369, 234, 344, 0, 69, 386, 446, 322, 330, 379, 395, 410, 484, 25, 78, 405, 58, 183, 68, 175, 314, 390, 37, 382, 337, 477, 142, 324, 433, 252, 371, 188, 298, 182, 313, 139, 31, 84, 239, 247, 420, 286, 217, 18, 454, 9, 178, 380, 403, 32, 320, 85, 27, 439, 352, 414, 240, 461, 388, 30, 115, 437, 202, 278, 56, 241, 1, 306, 127, 393, 347, 231, 400, 471, 64, 479, 121, 462, 416, 20, 263, 401, 398, 464, 268, 284, 77, 162, 36, 419, 176, 186, 287, 262, 469, 149, 408, 334, 466, 374, 237, 11, 168, 422, 294, 366, 165, 328, 358, 180, 174, 350, 349, 193, 256, 315, 412, 136, 481, 428, 112, 150, 19, 441, 38, 292, 222, 207, 317, 335, 254, 243, 311, 452, 301, 49, 448]

def partition_n(arr, n = 1):
	return [arr[i:i+n] for i in range(0, len(arr), n)]

def bytearray_to_uint(arr, size=8):
	spec = '_BH_I___Q'
	if spec[size] == '_' or size < 1 or size > 8:
		raise ValueError("Invalid size. Must be one of 1, 2, 4 or 8")
	while len(arr) % size != 0:
		arr.append(0)
	res = []
	for p in partition_n(arr, size):
		# '<' is LE, '>' is BE, '=' is native.
		res.append(unpack("<" + spec[size], bytes(p))[0])

	return res

#
# General params:
#		symbol-size: 2-7 bits
#			derived from input alphabet.
#		words-size: 8, 16, 32, 64 bits
#		include-null (add one to every symbol, to allow for \0)
#
def encode_string(S, word_size, sym_size, sym_map):
	spec = '_BH_I___Q'
	if spec[word_size] == '_' or word_size < 1 or word_size > 8:
		raise ValueError("Invalid word_size. Must be one of 1, 2, 4 or 8")
	res = []

	# Symbols per word
	spw = word_size*8 // sym_size

	for packet in partition_n(S, spw):
		bpacket = 0
		bs = ""
		for i, sym in enumerate(packet):
			bs += f"{sym_map.index(sym):05b},"
			bpacket = (bpacket << sym_size) | sym_map.index(sym)
		pw = unpack(">" + spec[word_size], bpacket.to_bytes(word_size))[0]
		print(f"{packet} => {bs} => {pw:0{word_size*2}x} => {pw:0{word_size*8}b}")
		for b in pw.to_bytes(word_size):
			res.append(b)

	return res

def calculate_symbol_size(s, reserve_symbols=0):
	return (len(set(s))+reserve_symbols).bit_length()

def get_symbol_map(s, reserve_symbols=0):
	return '\0' * reserve_symbols + "".join(list(sorted(set(s))))

def encode_ascii_5551bit(s):
	N = ceil(len(s) / 3)
	buf = bytearray(N)


def indices_to_bytearray(arr):
	buf = bytearray(ceil(max(arr) / 8))

	for idx in arr:
		byte_idx = idx // 8
		bit_idx = idx % 8
		# print(f"Setting bit {byte_idx * 8 + bit_idx} in byte {byte_idx}:{bit_idx}")
		buf[byte_idx] |= 1 << (bit_idx)
	return buf

#print(f"Input:\n{A}")
A = list(set(A))
print(f"Set of input:\n{A}")

size = 8
res = bytearray_to_uint(indices_to_bytearray(A), size)

print(f'Output: {len(res)} x {size*8}-bit words, or {len(res)*size} bytes.')

print("Binary:")
for word in res:
	print(f'{word:0{size*8}b}')

print("Hexadecimal:")
print(','.join(f'0x{a:x}' for a in res))

# TODO: Encode length table as bitmap (A_i + length[A_i])
# if max(L) == min(L): uniform length, table/bitmap not needed

print("String encoding:")

reserve_null = 0
input_size = len(S)
sym_size = calculate_symbol_size(S, reserve_null)
sym_map = get_symbol_map(S, reserve_null)
print(f"Symbol size: {sym_size}")
print(f"Symbol map: {sym_map} (len={len(sym_map)})")

res = encode_string(S, 2, sym_size, sym_map)
print(f"Hexadecimal (len={len(res)})")
print(','.join(f'0x{a:02x}' for a in res))

print(f"Input size: {input_size}, output size: {len(res)}, diff: {input_size-len(res)}")

