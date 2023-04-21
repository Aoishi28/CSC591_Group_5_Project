import math
from config import *

class Random:
    def __init__(self):
        self.seed = the['seed']
    
    def rint(self, lo=0, hi=1):
        return math.floor(0.5 + self.rand(lo, hi))

    def set_seed(self, value: int):
        self.seed = value

    def rand(self, lo=0, hi=1):
        self.seed = (16807 * self.seed) % 2147483647
        return lo + (hi - lo) * self.seed / 2147483647