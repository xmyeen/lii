# -*- coding:utf-8 -*-
#!/usr/bin/env Python

from enum import Enum,unique

@unique
class LsbReleaseDefs(Enum):
    DEBIAN = '/etc/lsb-release'
    REDHAT = '/etc/redhat-release'
    ALPINE = '/etc/alpine-release'