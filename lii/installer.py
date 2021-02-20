import configparser, subprocess, os, sys, warnings
from urllib.parse import urlparse
from functools import reduce
from typing import Dict,Any
from .datatype.app_prof import AppProf
from .datatype.image_prof import ImageProf
from .datatype.installation import APP_INSTALLATION_TYPES, GROUP_INSTALLATION_TYPES, BasicAppInstallation, BasicGroupInstallation
from .cfg.centos import CENTOS_CONFIGURATION_DFLT_DEF, CENTOS_DOCKER_TEMPALTE_DEF, CENTOS_INSTALLATION_TEMPALTE_DEF

# class MultiOrderedDict(OrderedDict):
#     def __setitem__(self, key, value):
#         if isinstance(value, list) and key in self:
#             self[key].extend(value)
#         else:
#             super(OrderedDict, self).__setitem__(key, value)
#     def keys(self):
#         return super(OrderedDict, self).keys()

INSTALLATION_WORK_DIRECTORY_DEF = '/tmp/installation-dir'

class Installer(object):
    DOCKERFILE_NAME = 'dockerfile'
    INSTALLATION_SCRIPT_NAME = 'inst.sh'
    ENTRYPOINT_FILE_NAME = 'app-entrypoint'

    def __init__(self, image_prof:ImageProf, server_port, localhub = None):
        self.__image_prof = image_prof

        self.__server_port = server_port 

        self.__localhub = localhub

        self.__excluding_group_names = []

        self.__app_profs = []

    # def __get_internal_mirror(self, name):
    #     return f'{self.get_internal_hub()}/{name}'
    # @property
    # def archive_home(self) -> str:
    #     return f'{self.__work_dir}/.archives'

    def get_app_home(self, app_prof: AppProf) -> str:
        if app_prof.version:
            return f'/opt/{app_prof.name}/{app_prof.version}'
        else:
            return f'/opt/{app_prof.name}'

    def __get_installation_configuration(self) -> Dict[str,Any]:
        return dict(
            image_from = self.__image_prof.image_from,
            image_maintainer = self.__image_prof.image_maintainer,
            image_name = self.__image_prof.name,
            http_server_port = self.__server_port,
            installation_file = self.INSTALLATION_SCRIPT_NAME,
            entrypoint_script_path = f'/sbin/{self.ENTRYPOINT_FILE_NAME}'
        )

    def __gen_installation_content(self) -> str:
        group_names = reduce(lambda s,p: s if p.group in s else s + [p.group], self.__app_profs, [])

        lines = []
        for group_name in group_names:
            if group_name in self.__excluding_group_names:
                continue

            if group_name in GROUP_INSTALLATION_TYPES:
                group = GROUP_INSTALLATION_TYPES[group_name]()
            else:
                group = BasicGroupInstallation()

            for prof in self.__app_profs:
                if prof.group == group_name:
                    if prof.name in APP_INSTALLATION_TYPES:
                        app = APP_INSTALLATION_TYPES[prof.name]()
                    else:
                        app = BasicAppInstallation()

                    app.prof = prof
                    app.home = f'/opt/{prof.name}'
                    app.building_work_dir = f'{INSTALLATION_WORK_DIRECTORY_DEF}/{prof.name}'
                    group.put_application(app)

            lines.append(str(group).strip())

        return '\n'.join(lines)

    def exec(self, workdir = None):
        # software = [ for cfg in ALL_SOFTWARE_CFGS if cfg not cfg.__excluding_software_cfgs]
        dockerfile_content, installation_content = None, None
        installation_cfg = self.__get_installation_configuration()

        if self.__image_prof.image_from.startswith('centos'):
            _, ver = self.__image_prof.image_from.split(':')

            if cfg := CENTOS_CONFIGURATION_DFLT_DEF.get(ver):
                cp = configparser.ConfigParser()
                cp.read_string(cfg)

                for sec in cp.sections():
                    prof = AppProf.load_configuration(
                        name = sec,
                        **dict(list(cp.items(sec)))
                    )

                    if self.__localhub and (url := prof.extension.get('url')):
                        parsed = parse.urlparse(url)
                        prof.extension.update(
                            url = f'{self.__localhub}/{prof.name}' + url[len(parsed.scheme) + 3 + len(parsed.netloc):]
                        )
                    
                    self.__app_profs.append(prof)

            # centos_version = subprocess.getoutput("cat /etc/centos-release | cut -f4 -d' ' | cut -f'1-2' -d'.'")
            if tmpl := CENTOS_DOCKER_TEMPALTE_DEF.get(ver):
                dockerfile_content = tmpl.format(**installation_cfg)

            if tmpl := CENTOS_INSTALLATION_TEMPALTE_DEF.get(ver):
                installation_content = tmpl.format(
                    application_installation_content = self.__gen_installation_content(),
                    **installation_cfg
                )
        # elif self.__image_prof.image_from.startswith('ubuntu'):
        #     _, ver = self.__image_prof.image_from.split(':')
        else:
            raise RuntimeError('Unsupported!')

        if not workdir or not os.path.exists(workdir):
            if dockerfile_content: print(dockerfile_content)
            if installation_content: print(installation_content)
        elif os.path.exists(workdir) and docker_file_content and installation_content:
            dockerfile_path = os.path.join(workdir, self.DOCKERFILE_NAME)
            installation_script_path = os.path.join(workdir, self.INSTALLATION_SCRIPT_NAME)
            
            with open(dockerfile_path, 'w', encoding='utf-8') as w1, open(installation_script_path, 'w', encoding='utf-8') as w2:
                w1.write(docker_file_content)
                w2.write(installation_content)

            p = subprocess.Popen([sys.executable, '-m', 'http.server', self.__server_port], cwd = workdir)
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
                    f'-t {self.__image_prof.name}:{self.__image_prof.latest}',
                    f'-f {dockerfile_path}',
                    "."
                ])

                print(f'Command: {cmdline}')
                if subprocess.call(cmdline, shell = True, cwd = workdir):
                    warnings.warn("Build image failed")
            finally:
                p.terminate()