# -*- coding:utf-8 -*-
#!/usr/bin/env Python

# from typing  import 
import traceback
from typing import Dict,Any,List,IO
from abc import ABCMeta, abstractclassmethod
from ..en.installation import InstallationMethodDefs

APP_INSTALLATION_TYPES = {}
GROUP_INSTALLATION_TYPES = {}

class BasicInstallation(object):
    def __init__(self):
        self.__home = None
        self.__work_dir = None
        # self.__configurer = None
        self.__configuration = None
        self.__previous_installation = None

    @property
    def name(self) -> str: return self.__configuration.get("name")

    def set_home(self, home:str): self.__home = home
    def get_home(self) -> str: return self.__home
    home = property(get_home, set_home, None, '部署目录')

    def set_work_dir(self, work_dir:str): self.__work_dir = work_dir
    def get_work_dir(self) -> str: return self.__work_dir
    work_dir = property(get_work_dir, set_work_dir, None, '工作目录')

    # def set_configurer(self, configurer): self.__configurer = configurer
    # def get_configurer(self): return self.__configurer
    # configurer = property(get_configurer, set_configurer, None, '配置器')

    def set_configuration(self, configuration): self.__configuration = configuration
    def get_configuration(self): return self.__configuration
    configuration = property(get_configuration, set_configuration, None, '配置')

    def set_previous_installation(self, previous_installation): self.__previous_installation = previous_installation
    def get_previous_installation(self): return self.__previous_installation
    previous_installation = property(get_previous_installation, set_previous_installation, None, '上一个安装器')

    def gen_env_content(self, output:IO, cfg:Dict[str,Any], **kwargs):
        if not cfg: return
        if not output: return

        lines = []

        c = self.configuration.copy()
        c.update(install_dir = self.home)
        c.update(kwargs)

        env = cfg.get('env')
        if env:
            for name,val in env.items():
                lines.append(f"export {name}={val.format(**c)}")

        catalog_cfg = cfg.get('catalog')
        if catalog_cfg:
            bin_dir,lib_dir = catalog_cfg.get('bin_dir'), catalog_cfg.get('lib_dir')
            if bin_dir:
                lines.append(f'export PATH=\\${{PATH}}:{bin_dir.format(**c)}')
            if lib_dir:
                lines.append(f'export LD_LIBRARY_PATH={lib_dir.format(**c)}:\\${{LD_LIBRARY_PATH}}')
        

        if lines:
            output.write('\n'.join([
                'cat >> ${HOME}/.bashrc << EOF',
                f'\n# {self.name}',
                *lines,
                'EOF'
            ]))
            output.write('\n')

    def gen_scripts_content(self, output:IO, dist_dir:str, cfg:Dict[str,Any], **kwargs):
        if not output: return

        c = self.configuration.copy()
        c.update(install_dir = self.home)
        c.update(dist_dir = dist_dir)
        c.update(kwargs)

        for script in cfg.get('scripts', []):
            output.write(script.format(**c))
            output.write('\n')

    def before(self, output:IO):
        pass

    def now(self, output:IO):
        pass

    def after(self, output:IO):
        pass

    def draw(self, output:IO):
        try:
            self.before(output)
        except:
            traceback.print_exc()
        try:
            self.now(output)
        except:
            traceback.print_exc()
        try:
            self.after(output)
        except:
            traceback.print_exc()
            
class BasicGroupInstallation(object):
    def __init__(self):
        self.__installations = []

    def put_installation(self, installation:BasicInstallation):
        self.__installations.append(installation)

    def before(self, output:IO):
        pass

    def after(self, output:IO):
        pass

    def draw(self, output:IO):
        try:
            self.before(output)
        except:
            traceback.print_exc()
        try:
            for installation in self.__installations:
                output.write(f'echo "--- {installation.name} install"\n')
                installation.draw(output)
        except:
            traceback.print_exc()
        try:
            self.after(output)
        except:
            traceback.print_exc()

# class GroupInstallationMeta(type):
#     def __new__(cls, *args, **kwargs):
#         c = type.__new__(cls, *args, **kwargs)
#         BasicGroupInstallation.TYPES
#         BasicGroupInstallation.TYPES.append(c)
#         return c

def app_d(name):
    def wrapping(cls):
        def wrapper(*arg, **kwargs):
            return cls(*args, **kwargs)
        
        APP_INSTALLATION_TYPES.update({ name : cls })
        return wrapper
    return wrapping

def group_d(name):
    def wrapping(cls):
        def wrapper(*arg, **kwargs):
            return cls(*args, **kwargs)

        GROUP_INSTALLATION_TYPES.update({ name : cls })
        return wrapper
    return wrapping