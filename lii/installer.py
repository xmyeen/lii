# -*- coding:utf-8 -*-
#!/usr/bin/env Python

import subprocess, os, sys, warnings, datetime, time, traceback, getopt
# from urllib.parse import urlparse
from functools import reduce
from typing import Dict,Any, List, IO
from .en.profile import ProfileDefs
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
        self.__workdir = f'/tmp/lii-{int(time.time())}'


    # def __get_internal_mirror(self, name):
    #     return f'{self.get_internal_hub()}/{name}'
    # @property
    # def archive_home(self) -> str:
    #     return f'{self.__work_dir}/.archives'


    def __get_installation_configuration(self) -> Dict[str,Any]:
        return dict(
            image_from = self.__configurer.image_from,
            image_maintainer = self.__configurer.image_maintainer,
            image_name = self.__configurer.name,
            http_server_addr = self.__server_addr,
            http_server_port = self.__server_port,
            installation_file = self.INSTALLATION_SCRIPT_NAME,
            entrypoint_script_path = f'/{self.ENTRYPOINT_FILE_NAME}'
        )

    def __gen_installation_content(self, io:IO) -> str:
        installer_cfg = self.__configurer.get_configuration(ProfileDefs.INSTALLATION_CONFIGURATION)
        
        group = {}
        for installation_cfg in installer_cfg.get("installations"):
            group_name = installation_cfg.get("group")
            if group_name in self.__configurer.image.excluding_installation_groups:
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
                        installation.work_dir = os.path.join(self.workdir, 'tmpdir', f'{name}.{type_}') 
                    elif 'ext' == type_:
                        installation = APP_INSTALLATION_TYPES.get(name)()
                        installation.home = installation_cfg.get('home') or os.path.join("/opt", name, version)
                        installation.work_dir = os.path.join(self.workdir, 'tmpdir', f'{name}.{type_}') 
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

        installation_content_io = StringIO()
        self.__gen_installation_content(installation_content_io)
        installation_content_io.seek(0)

        with \
        tempfile.NamedTemporaryFile() as installation_script_io, \
        tempfile.NamedTemporaryFile() as entrypoint_script_io, \
        tempfile.NamedTemporaryFile() as dockerfile_io: 
        
            # if "centos" == self.__configurer.lsb_release_name:
            # if self.__configurer.image_from.startswith('centos'):

            installation_script_io.write(
                self.__configurer.get_configuration(ProfileDefs.INSTALLATION).format(
                    mirror_content = "",
                    installation_content = sio.read()
                )
            )

            entrypoint_script_io.write(
                self.__configurer.get_configuration(ProfileDefs.DOCKER_ENTRYPOINT)
            )

            dockerfile_io.write(
                self.__configurer.get_configuration(ProfileDefs.DOCKER_DOCKERFILE).format(
                    image = self.__configurer.image,
                    installation_script = installation_script_io.name,
                    entrypoint_script = entrypoint_script_io.name
                )
            )

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
                    f'-t {self.__configurer.name}:{self.__configurer.version}',
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
                if 0 < value.index(":"): continue
                setting.lsb_release_name, setting.lsb_release_version = value.split(":")
            elif name in ("--maintainer"):
                setting.maintainer = value
            elif name in ("--name"):
                setting.set_full_name(value)
            elif name in ("--exclude"):
                setting.excluding_installation_groups.extend(value.split(','))
            elif name in ("--dockerfile", "--docker-entrypoint", "--installation", "--install-cfg"):
                setting.profile.update({ name[2:] : value })

        scan_module(__loader__.name.replace('__main__', "sh.installation"))

        configurer = Configurer(setting)
        configurer.init()
        installer = Installer(configurer)

        with tempfile.TemporaryDirectory() as td:
            Installer.exec(td)

    except SystemExit as ex:
        if 0 != ex.code:
            traceback.print_exc()
    except getopt.GetoptError as ex:
        traceback.print_exc()
        sys.exit(1)
    except BaseException as e:
        # warnings.warn(e)
        traceback.print_exc()