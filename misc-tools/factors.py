import numpy as np
"""
If you want a module which does not have an infinitely repeating decimal, you must
ensure the module equation m * (np1 - nr1)/(np2 - nr2) has a quotient which has prime
factors of 2 and 5.

This lists all the prime factors between 0 and 120
"""
nums = []
for n in range(0,10):
    for m in range(0,10):
        nums.append(2**n * 5**m)
nums.sort()
nums = np.array(nums)
print(nums[nums<=120])

