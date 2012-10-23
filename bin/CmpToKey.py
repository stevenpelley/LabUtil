#!/usr/bin/python
#
# script to provide cmp() like interface to sorting in python3
# recall that cmp(x,y) is negative if x < y, 0 if equal, positive if x > y
# think of cmp as a subtraction operation

def cmp_to_key(mycmp):
  'Convert a cmp= function into a key= function'
  class K(object):
    def __init__(self, obj, *args):
      self.obj = obj
    def __lt__(self, other):
      return mycmp(self.obj, other.obj) < 0
    def __gt__(self, other):
      return mycmp(self.obj, other.obj) > 0
    def __eq__(self, other):
      return mycmp(self.obj, other.obj) == 0
    def __le__(self, other):
      return mycmp(self.obj, other.obj) <= 0  
    def __ge__(self, other):
      return mycmp(self.obj, other.obj) >= 0
    def __ne__(self, other):
      return mycmp(self.obj, other.obj) != 0
  return K

def map_and_cmp_to_key(mapfn, mycmp):
  "Apply a function before using mycmp to sort"
  class K(object):
    def __init__(self, obj, *args):
      self.obj = mapfn(obj)
    def __lt__(self, other):
      return mycmp(self.obj, other.obj) < 0
    def __gt__(self, other):
      return mycmp(self.obj, other.obj) > 0
    def __eq__(self, other):
      return mycmp(self.obj, other.obj) == 0
    def __le__(self, other):
      return mycmp(self.obj, other.obj) <= 0  
    def __ge__(self, other):
      return mycmp(self.obj, other.obj) >= 0
    def __ne__(self, other):
      return mycmp(self.obj, other.obj) != 0
  return K
