# -*- coding:utf-8 -*-
#!/usr/bin/env Python

from enum import Enum,unique

@unique
class CompressionDefs(Enum):
    XZ = ".tar.xz"
    GZ = ".tar.gz"
    BZ = ".tar.bz"
    BZ2 = ".tar.bz2"
    Z = ".tar.Z"
    ZIP = ".zip"
    RPM = ".rpm"
