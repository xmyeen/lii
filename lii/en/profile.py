# -*- coding:utf-8 -*-
#!/usr/bin/env Python


import os
from enum import Enum,unique

@unique
class ProfileDefs(Enum):
    DOCKER_DOCKERFILE = 'dockerfile'
    DOCKER_ENTRYPOINT = 'docker-entrypoint'
    INSTALLATION = 'installation'
    INSTALLATION_CONFIGURATION = 'install-cfg'

    @staticmethod
    def from_file(file_path:str):
        for nm,en in ProfileDefs.__members__.items():
            if en.value == os.path.basename(file_path):
                return en
        return None

    @staticmethod
    def get_all_files():
        return [ en.value for nm,en in ProfileDefs.__members__.items() ]