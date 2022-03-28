# -*- coding:utf-8 -*-
#!/usr/bin/env Python

import subprocess, os, sys, warnings, datetime, time, traceback, getopt, tempfile, json
from io import StringIO
# from urllib.parse import urlparse
from functools import reduce
from typing import Dict,Any, List, IO
from .en.profile import ProfileDefs
from .util.semver_utils import cov_version,cmpexp
from .util.module_utils import scan_module
from .datatype.setting import Setting
from .datatype.installation import APP_INSTALLATION_TYPES, GROUP_INSTALLATION_TYPES, BasicInstallation, BasicGroupInstallation
from .configurer import Configurer
from .sh.installation.common import DnfInstallation, BinaryInstallation
# from .cfg.centos import CENTOS_CONFIGURATION_DFLT_DEF, CENTOS_DOCKER_TEMPALTE_DEF, CENTOS_INSTALLATION_TEMPALTE_DEF

# class MultiOrderedDict(OrderedDict):
#     def __setitem__(self, key, value):
#         if isinstance(value, list) and key in self:
#             self[key].extend(value)
#         else:
#             super(OrderedDict, self).__setitem__(key, value)
#     def keys(self):
#         return super(OrderedDict, self).keys()

# INSTALLATION_WORK_DIRECTORY_DEF = '/tmp/installation-dir'

class Installer(object):
    DOCKERFILE_NAME = 'dockerfile'
    INSTALLATION_SCRIPT_NAME = 'inst.sh'
    ENTRYPOINT_FILE_NAME = 'docker-entrypoint'

    def __init__(self, configurer:Configurer):
        self.__configurer = configurer
        self.__installer_workdir = f'/tmp/lii-{int(time.time())}'


    # def __get_internal_mirror(self, name):
    #     return f'{self.get_internal_hub()}/{name}'
    # @property
    # def archive_home(self) -> str:
    #     return f'{self.__work_dir}/.archives'

    def __gen_mirror_content(self, io:IO):
        installer_cfg = json.loads(self.__configurer.get_configuration(ProfileDefs.INSTALLATION_CONFIGURATION))
        for mirror_cfg in installer_cfg.get(self.__configurer.lsb_release_name, {}).get('mirrors', []):
            if not cmpexp(self.__configurer.lsb_release_version, mirror_cfg.get('version')):
                continue

            major,minor,patch,*_ = cov_version(self.__configurer.lsb_release_version).split('.')
            file = mirror_cfg.get('file').format(
                lsb_release_name = self.__configurer.lsb_release_name,
                lsb_release_version = dict(
                    major = major,
                    minor = minor,
                    patch = patch
                )
            )

            name = mirror_cfg.get('name')
            if 'centos' == self.__configurer.lsb_release_name:
                io.write(f'# --- Add {name} repository\n')
                io.write(f"curl -k -s -L -o /etc/yum.repos.d/{name}.repo {file}\n")


    def __gen_installation_content(self, io:IO):
        installer_cfg = json.loads(self.__configurer.get_configuration(ProfileDefs.INSTALLATION_CONFIGURATION))
        
        group = {}
        for installation_cfg in installer_cfg.get("installations"):
            group_name = installation_cfg.get("group")
            if group_name in self.__configurer.setting.excluding_installation_groups:
                #不包含的软件组，不进行安装
                continue
            if group_name not in group: group.update({ group_name : [] })
            group[group_name].append(installation_cfg)

        for group_name, installation_cfgs in group.items():
            if group_name in GROUP_INSTALLATION_TYPES:
                group = GROUP_INSTALLATION_TYPES[group_name]()
            else:
                group = BasicGroupInstallation()


            for installation_cfg in installation_cfgs:
                name = installation_cfg.get("name")
                version = installation_cfg.get("version", datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
                previous_installation = None
                for type_ in installation_cfg.get("install").split('+'):
                    if 'dnf' == type_:
                        installation = DnfInstallation()
                        installation.home = installation_cfg.get('home')
                    elif 'bin' == type_:
                        installation = BinaryInstallation()
                        installation.home = installation_cfg.get('home') or os.path.join("/opt", name, version)
                        installation.work_dir = os.path.join(self.__installer_workdir, 'tmpdir', f'{name}.{type_}') 
                    elif 'ext' == type_:
                        installation = APP_INSTALLATION_TYPES.get(name)()
                        installation.home = installation_cfg.get('home') or os.path.join("/opt", name, version)
                        installation.work_dir = os.path.join(self.__installer_workdir, 'tmpdir', f'{name}.{type_}') 
                    else:
                        print(f"No installation found for {type_}")
                        break
                    
                    installation.configuration = installation_cfg
                    installation.previous_installation = previous_installation
                    group.put_installation(installation)
                    previous_installation = installation

            group.draw(io)

    def exec(self, workdir = None):
        # software = [ for cfg in ALL_SOFTWARE_CFGS if cfg not cfg.__excluding_software_cfgs]
        dockerfile_content, installation_content = None, None
        # installation_cfg = self.__get_installation_configuration()

        mirror_content_io = StringIO()
        self.__gen_mirror_content(mirror_content_io)
        mirror_content_io.seek(0)

        installation_content_io = StringIO()
        self.__gen_installation_content(installation_content_io)
        installation_content_io.seek(0)

        with \
        open(os.path.join(workdir, '1.sh'), 'w', encoding='utf-8') as installation_script_io, \
        open(os.path.join(workdir, '2.sh'), 'w', encoding='utf-8') as entrypoint_script_io, \
        tempfile.NamedTemporaryFile('w', encoding='utf-8') as dockerfile_io: 

            installation_script_io.write(
                self.__configurer.get_configuration(ProfileDefs.INSTALLATION).format(
                    mirror_content = mirror_content_io.read(),
                    installation_content = installation_content_io.read()
                )
            )
            installation_script_io.flush()

            entrypoint_script_io.write(
                self.__configurer.get_configuration(ProfileDefs.DOCKER_ENTRYPOINT)
            )
            entrypoint_script_io.flush()

            dockerfile_io.write(
                self.__configurer.get_configuration(ProfileDefs.DOCKER_DOCKERFILE).format(
                    image = self.__configurer.setting.get_image(),
                    installation_script = os.path.basename(installation_script_io.name),
                    entrypoint_script = os.path.basename(entrypoint_script_io.name),
                    installation_label = 'lii'
                )
            )
            dockerfile_io.flush()

            try:
                cmdline = ' '.join([
                    'docker',
                    'build',
                    '--force-rm',
                    # '--pull',
                    '--no-cache',
                    '--build-arg HTTP_PROXY=${HTTP_PROXY}',
                    '--build-arg HTTPS_PROXY=${HTTPS_PROXY}',
                    # f'--build-arg builder_sh={os.path.basename(software_script_f.name)}',
                    f'-t {self.__configurer.setting.name}:{self.__configurer.setting.tag}',
                    f'-f {dockerfile_io.name}',
                    "."
                ])

                print(f'Command: {cmdline}')
                if subprocess.call(cmdline, shell = True, cwd = workdir):
                    warnings.warn("Build image failed")
            # finally:
            #     p.terminate()
            except:
                traceback.print_exc()

def usage(setting:Setting):
    return "\n".join([
        f"lii installer [option]",
        f"-h, --help                           Print usage",
        f"--from=<str>                         Specify parent image name. Default: '{setting.from_}'",
        f"--maintainer=<str>                   Specify maintainer. Default: '{setting.maintainer}'",
        f"--name=<str>                         Specify name. Default: '{setting.get_full_name()}'",
        f"--exclude=<group1,group2,...>        Excluding groups. Such as \"A,B,C\". Default: {','.join(setting.excluding_installation_groups)}",
        f"--lsb-release=<str>                  Specify os release. Such as 'centos:7'",
        f"--install-cfg=<path>                 Customize install configuration",
        f"--dockerfile=<path>                  Customize dockerfile template",
        f"--docker-entrypoint=<path>           Customize docker-entrypoint script",
        f"--installation=<path>                Customize installation script"
    ])

def main():
    try:
        setting = Setting()

        opts, args = getopt.getopt(sys.argv[2:], "h", ["help", "from=", "lsb-release=", "maintainer=", "name=", "exclude=", "install-cfg=", "dockerfile=", "docker-entrypoint=", "installation="])
        for name, value in opts:
            if name in ("-h", "--help"):
                print(usage(setting))
                sys.exit(0)
            elif name in ("--from"):
                setting.from_ = value
            elif name in ("--lsb-release"):
                if 0 > value.index(":"): continue
                setting.lsb_release_name, setting.lsb_release_version = value.split(":")
            elif name in ("--maintainer"):
                setting.maintainer = value
            elif name in ("--name"):
                setting.set_full_name(value)
            elif name in ("--exclude"):
                setting.excluding_installation_groups.extend(value.split(','))
            elif name in ("--dockerfile", "--docker-entrypoint", "--installation", "--install-cfg"):
                setting.profile.update({ name[2:] : value })

        # print(__loader__.name)
        # scan_module(__loader__.name.replace('__main__', "sh.installation"))
        scan_module('lii.sh.installation')

        configurer = Configurer(setting)
        configurer.init()
        installer = Installer(configurer)

        with tempfile.TemporaryDirectory() as td:
            installer.exec(td)

    except SystemExit as ex:
        if 0 != ex.code:
            traceback.print_exc()
    except getopt.GetoptError as ex:
        traceback.print_exc()
        sys.exit(1)
    except BaseException as e:
        # warnings.warn(e)
        traceback.print_exc()