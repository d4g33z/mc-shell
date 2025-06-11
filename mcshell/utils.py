import collections
from mcshell.constants import *

def translate_by_n(v, direction, n):
    print(direction)
    _v = v.clone()
    if direction == 'NORTH':
        _v.z -= n
    elif direction == 'SOUTH':
        _v.z += n
    elif direction == 'EAST':
        _v.x += n
    elif direction == 'WEST':
        _v.x -= n
    return _v

def flatten(l):
    for e in l:
        if isinstance(e, collections.Iterable) and not isinstance(e, str):
            for ee in flatten(e): yield ee
        else: yield e

def flatten_parameters_to_string(l):
    return ",".join(map(str, flatten(l)))
