#!/usr/bin/python
# test out cmp_to_key and map_and_cmp_to_key

import sys
sys.path.append("../../bin")
import CmpToKey
import random

def rev_cmp(x,y):
  return y - x

# 10 is the minimum, otherwise normal compare
def ten_min_cmp(x,y):
  if 10 in [x,y] and x != y:
    if x == 10:
      return -1
    else:
      return 1
  else:
    return x-y

if __name__ == "__main__":
  # test compare functions
  assert rev_cmp(1,2) == 1
  assert rev_cmp(2,2) == 0
  assert rev_cmp(2,1) == -1

  assert ten_min_cmp(1,2) == -1
  assert ten_min_cmp(2,2) == 0
  assert ten_min_cmp(2,1) == 1
  assert ten_min_cmp(5,10) == 1
  assert ten_min_cmp(10,5) == -1
  assert ten_min_cmp(10,10) == 0

  data = list(range(9))
  s = "{:>25}: {!s}"
  print(s.format("data", data))
  random.shuffle(data)
  print(s.format("shuffled", data))
  print(s.format("sorted", sorted(data)))
  print(s.format("sorted, reverse", sorted(data, reverse=True)))
  print(s.format("sorted, reverse_cmp", sorted(data, key=CmpToKey.cmp_to_key(rev_cmp))))
  # 8 should appear first -- 8+2 = 10, and 10 is the minimum value with ten_min_cmp()
  print(s.format("sorted, map and ten_min", sorted(data, key=CmpToKey.map_and_cmp_to_key(lambda x: x+2, ten_min_cmp))))
  print(s.format("shuffled", data))
