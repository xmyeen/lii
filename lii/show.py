# -*- coding:utf-8 -*-
#!/usr/bin/env Python

import sys,os,traceback,json, getopt
from .en.profile import ProfileDefs
from .datatype.setting import Setting
from .configurer import Configurer

def usage(setting:Setting):
    return "\n".join([
        f"lii show [option] {'/'.join(ProfileDefs.get_all_files())}",
        f"-h, --help                    Print usage",
        f"--from=<str>                  Specify parent image name. Default: '{setting.from_}'",
        f"--maintainer=<str>            Specify maintainer. Default: '{setting.maintainer}'",
        f"--name=<str>                  Specify name. Default: '{setting.get_full_name()}'",
        f"--lsb-release=<Name:Version>  Specify os release. Such as 'centos:7'",
        "-o, --output=<file>            Output into this file"
    ])

def main():
    try:
        setting, cfg = Setting(), {}

        opts, args = getopt.getopt(sys.argv[2:], "ho:", ["help", "from=", "lsb-release=", "maintainer=", "name=", "output="])
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
            elif name in ("-o", "--output"):
                cfg.update(output = value)

        configurer = Configurer(setting)
        configurer.init()
        for arg in args:
            content = configurer.get_configuration(ProfileDefs.from_file(arg))
            f = open(cfg.get("output"), 'w', encoding='utf-8') if cfg.get("output") else sys.stdout
            f.write('-'*3 + ' ' + arg)
            f.write('\n')
            f.write(content)
            f.write('\n')
            f.write('-'*3 + '-' + '-' * len(arg))

    except SystemExit as ex:
        if 0 != ex.code:
            traceback.print_exc()
    except getopt.GetoptError as ex:
        traceback.print_exc()
        sys.exit(1)
    except BaseException as e:
        # warnings.warn(e)
        traceback.print_exc()