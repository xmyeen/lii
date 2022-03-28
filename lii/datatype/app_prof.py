from typing import Dict
from dataclasses import dataclass, asdict, field as asfield

@dataclass
class AppProf(object):
    name: str
    version : str
    install : str
    group : str
    extension : Dict[str,str] = asfield(default_factory = dict)

    @staticmethod
    def load_configuration(group, install, name, version = None, **kwargs):
        if not name:
            raise RuntimeError("The 'name' parameter is missing or null")

        if not install:
            raise RuntimeError("The 'install' parameter is missing or null")

        if not group:
            raise RuntimeError("The 'group' parameter is missing or null")

        prof =  AppProf(
            name = name,
            version = version,
            install = install,
            group = group
        )

        cfg = asdict(prof)

        prof.extension.update({ k : v and v.format(**cfg) for k,v in kwargs.items() })

        return prof