# -*- coding:utf-8 -*-
#!/usr/bin/env Python

import os,subprocess,json, enum, tempfile, csv
from typing import Dict,Any
from .en.lsb_release import LsbReleaseDefs
from .en.installation import InstallationMethodDefs
from .en.profile import ProfileDefs
from .util.semver_utils import cmpexp
from .datatype.setting import Setting
from .datatype.semver import  semver

LSB_LOOK_SCRIPTS_DEF = f'''
if [ -e {LsbReleaseDefs.REDHAT.value} ]
then 
  cat {LsbReleaseDefs.REDHAT.value} | awk '{{print $1 "-" $4'}}
elif [ -e {LsbReleaseDefs.DEBIAN.value} ]
then
  cat {LsbReleaseDefs.DEBIAN.value}  | awk -F'=' 'NR == 1 || NR == 2 {{print $2}}' | paste -sd "-"
elif [ -e {LsbReleaseDefs.ALPINE.value} ]
then 
   awk '{{print "alpine" "-" $1}}' {LsbReleaseDefs.ALPINE.value}
fi 
'''

class Configurer(object):
    def __init__(self, setting:Setting):
        self.__setting = setting or Setting()

        self.__lsb_release_name = setting.lsb_release_name
        self.__lsb_release_version = setting.lsb_release_version

        # self.__installation_configuration = None
        self.__data_file = {}

    @property
    def setting(self):
        return self.__setting

    @property
    def lsb_release_name(self):
        return self.__lsb_release_name

    @property
    def lsb_release_version(self):
        return self.__lsb_release_version

    def __load_data_file(self):
        data_root = os.path.join(os.path.dirname(__file__), 'data', "docker")
        data_db = os.path.join(data_root, 'data.csv')

        self.__data_file.update({
            ProfileDefs.INSTALLATION_CONFIGURATION.value : os.path.join(data_root, self.__lsb_release_name, "install-cfg.json")
        })
        
        with open(data_db, 'r', encoding='utf-8') as r:
            reader = csv.reader(r)
            for line in reader:
                type_, os_, p, exp = line
                if os_ != self.lsb_release_name:
                    continue

                if not cmpexp(str(self.lsb_release_version), exp):
                    continue

                self.__data_file.update({ type_ : os.path.join(data_root, p) })

    def init(self):
        if not self.__lsb_release_name or not self.__lsb_release_version:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8') as tf:
                tf.write('#!/bin/sh\n')
                tf.write(LSB_LOOK_SCRIPTS_DEF)
                tf.flush()
                lsb_release_str = subprocess.getoutput(f'docker run --rm -it -v {os.path.abspath(tf.name)}:/run.sh {self.setting.from_} sh /run.sh')
                if not lsb_release_str:
                    raise RuntimeError('No lsb_release found')

                self.__lsb_release_name, version_str = lsb_release_str.lower().split('-')
                self.__lsb_release_version = semver.from_str(version_str)

        self.__load_data_file()

    def get_configuration(self, profile_en:ProfileDefs) -> str:
        file = self.setting.profile.get(profile_en.value) or self.__data_file.get(profile_en.value)
        with open(file, 'r', encoding='utf-8') as r:
            return r.read()