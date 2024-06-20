# Approximate Shortest Superstring Generator

A Python tool for generating approximate [shortest common superstrings](https://en.wikipedia.org/wiki/Shortest_common_supersequence#Shortest_common_superstring) for some input,
using the algorithm Greedy[^Blum1994][^Kaplan2004].

A _superstring_ is simply a string that contains some set of two or more strings as substrings. Though one
can trivially be generated by just concatenating the input strings, we're usually interested in finding
a more _optimal_ solution, one which exploits the fact that strings in the input set may overlap.

Finding the _shortest_ such superstring is NP-hard, but there are algorithms to approximate it,
the simplest of which is called 'Greedy'.

All code is provided under the [MIT License](LICENSE).

_WARNING: While this note is here, I may force-push to master_

## Discussion

The concept of this tool is simple; an input file with the string set to optimize is provided, and the tool generates an approximate
superstring, plus some auxiliary information and tables that may or may not be useful.

This repository is an artifact of an ultimately failed experiment to see if superstrings could be used to size-optimize the
mnemonics table of a C64 assembler or disassembler. I may still write it up at some point, though that seems increasingly unlikely.

As of writing, the tool is extremely hacky, and other than accepting a file name, you must change the source in order to
change options. Much of the output could be wrong, and some of the configuration options are broken or interact in
non-obvious ways. Caveat emptor indeed.

I've been meaning to essentially rewrite it, but since it's been more than six months now I'm just
releasing it as-is.

## Usage

```bash
$ ./superstring.py examples/MOS6510-mnem-basic.txt
Removing duplicate entries from input
256 strings (total len=768, min/max len=3/3) in input, 57 unique strings (total len=171) remain.
['BRK', 'ORA', 'JAM', 'ASL', 'PHP', 'BPL', 'CLC', 'JSR', 'AND', 'BIT', 'ROL', 'PLP', 'BMI', 'SEC', 'RTI', 'EOR', 'LSR', 'PHA', 'JMP', 'BVC', 'CLI', 'RTS', 'ADC', 'ROR', 'PLA', 'BVS', 'SEI', 'STA', 'STY', 'STX', 'DEY', 'TXA', 'BCC', 'TYA', 'TXS', 'LDY', 'LDA', 'LDX', 'TAY', 'TAX', 'BCS', 'CLV', 'TSX', 'CPY', 'CMP', 'DEC', 'INY', 'DEX', 'BNE', 'CLD', 'CPX', 'SBC', 'INC', 'INX', 'NOP', 'BEQ', 'SED']
Generated Superstring is 127 characters, saving 641/44:
BRKTAXBVCLIJMPSTAYRORTSXSTXADEYSECMPLDXBEQSEINYBVSBCCPXBCSTYAJSRTINCLDYBITXSEDECLCPYBPLPLABMINXNOPHPHADCLVJAMBNEORASLSROLDANDEX
Shannon entropy(s): 4.202758 bits/symbol, 533.7502 bits (67 bytes)
Alphabet size=21 (5 bits/symbol):
ABCDEHIJKLMNOPQRSTVXY
The 256 verified ok offsets (~1681/224*8 bits, min unit=7 bits) are:
[0, 112, 106, 106, 106, 112, 114, 106, 97, 112, 114, 106, 106, 112, 114, 106, 84, 112, 106, 106, 106, 112, 114, 106, 79, 112, 106, 106, 106, 112, 114, 106, 61, 122, 106, 106, 71, 122, 118, 106, 85, 122, 118, 106, 71, 122, 118, 106, 90, 122, 106, 106, 106, 122, 118, 106, 31, 122, 106, 106, 106, 122, 118, 106, 63, 111, 106, 106, 106, 111, 116, 106, 99, 111, 116, 106, 11, 111, 116, 106, 6, 111, 106, 106, 106, 111, 116, 106, 8, 111, 106, 106, 106, 111, 116, 106, 20, 101, 106, 106, 106, 101, 18, 106, 87, 101, 18, 106, 11, 101, 18, 106, 47, 101, 106, 106, 106, 101, 18, 106, 42, 101, 106, 106, 106, 101, 18, 106, 106, 14, 106, 106, 57, 14, 24, 106, 28, 106, 25, 106, 57, 14, 24, 106, 50, 14, 106, 106, 57, 14, 24, 106, 58, 14, 73, 106, 106, 14, 106, 106, 68, 120, 36, 106, 68, 120, 36, 106, 15, 120, 3, 106, 68, 120, 36, 106, 55, 120, 106, 106, 68, 120, 36, 106, 103, 120, 21, 106, 68, 120, 36, 106, 81, 33, 106, 106, 81, 33, 77, 106, 44, 33, 124, 106, 81, 33, 77, 106, 109, 33, 106, 106, 106, 33, 77, 106, 67, 33, 106, 106, 106, 33, 77, 106, 52, 49, 106, 106, 52, 49, 65, 106, 92, 49, 95, 106, 52, 49, 65, 106, 39, 49, 106, 106, 106, 49, 65, 106, 75, 49, 106, 106, 106, 49, 65, 106]
min/max offset=0/124
Superstring: 127 + 224 + 0 = 351 bytes.
Direct: 768 bytes.
```

The thing you probably care about is the line after "Generated Superstring..."

The offsets provide a mapping from the index of a string in the input set, to the start of that string within the superstring.

In the case that the input strings are not all of equal length, a length table will be generated too.

The order of the input to the algorithm matters, and some orderings will generate a better/worse superstring. To this
end it can be useful to set the `doshuffle` flag to True and rerunning the tool a couple of times.

The `dosort` option will sort the input by frequency, which should reduce the size of the offset table.

With minor changes the input can be transformed into binary strings, which can result in further optimized output, at the cost
of more complicated decoding of course.

## Python Superstring Library API

`generate_superstring(list) -> str`
: Accepts a list of strings, returns the approximate superstring using the default algorithm, first processing the input to make it substring-free.

`greedy(list) -> str`
: Accepts a list of strings, return the approximate superstring as generated by algorithm Greedy.

`make_substring_free(list) -> list`
: For Greedy to work as originally specified, its input must be _substring-free_, i.e contain no elements that are substrings of one another. This function will process a list to ensure this pre-condition is true.

See the [ssp.py source code](ssp.py) for details.

### Example API Usage

```python
arr = ['n', 'ora', 'bne', 'eor']
res = generate_superstring(arr)
# res=bneora
```

## TODO

* Verify that the type-spec in ssp.py is actually correct.

[^Blum1994]: "[Linear Approximation of Shortest Superstrings](https://ir.cwi.nl/pub/1422/1422D.pdf)", Blum et al., 1994.
[^Kaplan2004]: "[The Greedy Algorithm for Shortest Superstrings](https://doi.org/10.1016/j.ipl.2004.09.012)", Kaplan & Shafrir, 2004.
