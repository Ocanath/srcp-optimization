import numpy as np

nums = []
for n in range(0,10):
    for m in range(0,10):
        nums.append(2**n * 5**m)
nums.sort()
nums = np.array(nums)
print(nums[nums<=120])
