# -*- coding:utf-8 -*-
#!/usr/bin/env Python

from enum import Enum,unique

@unique
class InstallationMethodDefs(Enum):
    dnf = 1
    bin = 2
    ext = 3