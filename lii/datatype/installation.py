#!/env/Python

# from typing  import 
from abc import ABCMeta, abstractclassmethod
from ..en.installation import InstallationMethodDefs
from .app_prof import AppProf

APP_INSTALLATION_TYPES = {}
GROUP_INSTALLATION_TYPES = {}

class BasicAppInstallation(object):
    def __init__(self):
        self.__home = None
        self.__building_work_dir = None
        self.__prof = None

    def set_home(self, home:str): self.__home = home
    def get_home(self) -> str: return self.__home
    home = property(get_home, set_home, None, '配置')

    def set_building_work_dir(self, building_work_dir:str): self.__building_work_dir = building_work_dir
    def get_building_work_dir(self) -> str: return self.__building_work_dir
    building_work_dir = property(get_building_work_dir, set_building_work_dir, None, '编译工作目录')

    def set_prof(self, prof:AppProf): self.__prof = prof
    def get_prof(self) -> AppProf: return self.__prof
    prof = property(get_prof, set_prof, None, '配置')

    def gen_rpm_content(self) -> str:
        '''生成rpm安装的脚本段
        '''
        names, yums, rpms = [], [], []

        if self.__prof.install == InstallationMethodDefs.yum.name:
            if rpm_name := self.__prof.extension.get('rpms'):
                yums.append(rpm_name)
            elif self.__prof.version:
                yums.append(f"{self.__prof.name}-{self.__prof.version}")
            else:
                yums.append(self.__prof.name)

        if self.__prof.install == InstallationMethodDefs.rpm.name:
            if rpm_name := self.__prof.extension.get('rpms'):
                yums.append(rpm_name)
            elif self.__prof.version:
                rpms.append(f"{self.__prof.name}-{self.__prof.version}")
            else:
                rpms.append(self.__prof.name)

        names.append(self.__prof.name)

        return '\n'.join([
            f'#--- Install {"".join(names)}' if names else '',
            f'yum install -y {"".join(yums)}' if yums else '',
            f'rpm -ivh {"".join(rpms)}' if rpms else ''
        ]).strip()

    def __str__(self) -> str:
        return '\n'.join([self.before(), self.now(), self.after()]).strip()

    def before(self) -> str:
        return ''

    def now(self) -> str:
        if self.__prof.install == InstallationMethodDefs.yum.name:
            return self.gen_rpm_content()
        elif self.__prof.install == InstallationMethodDefs.rpm.name:
            return self.gen_rpm_content()
        else:
            return ''

    def after(self) -> str:
        return ''

class BasicGroupInstallation(object):
    def __init__(self):
        self.__home = None
        self.__installations = []

    def set_home(self, home:str): self.__home = home
    def get_home(self) -> str: return self.__home
    home = property(get_home, set_home, None, '根目录')

    def put_application(self, installation:BasicAppInstallation):
        self.__installations.append(installation)

    def __str__(self) -> str:
        return '\n'.join([self.before(), self.now(), self.after()]).strip()

    def before(self) -> str:
        return ''

    def now(self) -> str:
        return '\n'.join([ str(i) for i in self.__installations ])

    def after(self) -> str:
        return ''

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