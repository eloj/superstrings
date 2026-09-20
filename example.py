import ssp

arr = ["CABABAB", "BABABA", "ABABABC" ]

res = ssp.generate_superstring(arr)
print(res)

res = ssp.generate_superstring(arr, ssp.brute)
print(res)
