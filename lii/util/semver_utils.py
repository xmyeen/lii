# -*- coding:utf-8 -*-
#!/usr/bin/env Python

import re
from distutils.version import StrictVersion

def __cmp_0(a, b):
    return bool(a > b) - bool(a < b)

def __cov_expression(v, exp):
    op, v2 = re.findall(r"([><=]+)\s*(\d+\.?\d*\.?\d*)", exp)[0]
    return v, op, v2

def cov_version(ver):
    v = str(ver)
    if re.fullmatch(f'\d+\.\d+\.\d+', v): return v
    elif re.fullmatch(f'\d+\.\d+', v): return f'{v}.0'
    elif re.fullmatch(f'\d+', v): return f'{v}.0.0'
    else: raise RuntimeError(f"Invalid version number: {v}")

def cmpver(v1, v2, op = None): 
    _map = {
        '<': [-1],
        'lt': [-1],
        '<=': [-1, 0],
        'le': [-1, 0],
        '>': [1],
        'gt': [1],
        '>=': [1, 0],
        'ge': [1, 0],
        '==': [0],
        'eq': [0],
        '!=': [-1, 1],
        'ne': [-1, 1],
        '<>': [-1, 1]
    }

    v1 = StrictVersion(cov_version(v1))
    v2 = StrictVersion(cov_version(v2))
    result = __cmp_0(v1, v2)
    if op:
        assert op in _map.keys()
        return result in _map[op]
    return result

def cmpexp(v, exp):
    def _cmp_single_exp(v, exp):
        if not exp: return False
        v1, op, v2 = __cov_expression(v, exp)
        return cmpver(v1, v2, op)
    return all([ _cmp_single_exp(v, e.strip()) for e in exp.split(',') ])