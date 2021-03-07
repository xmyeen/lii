# -*- coding:utf-8 -*-
#!/usr/bin/env Python

from dataclasses import dataclass
from ..util.simver_util import cov_version

@dataclass
class SimVer(object):
    major: int = 0
    minor: int = 0
    patch: int = 0

    @staticmethod
    def from_str(v:str) -> 'SimVer':
        sv = SimVer()
        sv.major, sv.minor, sv.patch, *_ = cov_version(v).split(".")
        return sv

    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'