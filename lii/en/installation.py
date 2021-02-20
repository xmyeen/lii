from enum import Enum,unique

@unique
class InstallationMethodDefs(Enum):
    yum = 1
    http = 2
    filesystem = 3
    rpm = 4
    custom = 5