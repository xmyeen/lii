from dataclasses import dataclass, field
from typing import List,Dict

@dataclass
class Setting(object):
    from_: str = "centos:7"
    lsb_release_name: str = None
    lsb_release_version: str = None
    maintainer: str = "xmyeen xmyeen@sina.com.cn"
    
    mirror: str = None
    repo: str = "xmyeen"
    name: str = "lii"
    tag: str = "1.0.0"

    excluding_installation_groups:List[str] = field(default_factory = list)
    profile: Dict[str,str] = field(default_factory = dict)

    def get_image(self) -> Dict[str,str]:
        return dict(
            FROM = self.from_,
            MAINTAINER = self.maintainer,
            fullname = self.get_full_name()
        )

    def get_full_name(self):
        if self.mirror:
            return f'{self.mirror}/{self.repo}/{self.name}:{self.tag}'
        else:
            return f'{self.name}:{self.tag}'

    def set_full_name(self, full_name:str):
        mirror_repo_name, self.tag = full_name.split(':')
        *others, self.name = mirror_repo_name.split('/')
        
        if not others: self.mirror, self.repo = None, None
        elif 1 == len(others): self.mirror, self.repo = None, others[0]
        else: self.mirror, self.repo = '/'.join(others[0:-1]), others[-1]