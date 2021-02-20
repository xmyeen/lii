import sys, warnings, traceback, getopt, tempfile
from .util.module_utils import scan_module
from .datatype.image_prof import ImageProf
from .installer import Installer

APP_CONFIGURATION_DEF = dict(
    name = 'lii', version = 'latest', 
    image_from = "centos:7",
    image_maintainer = "xmyeen xmyeen@sina.com.cn",
    port = 80, 
    isdebug = False
)

USAGE_DEF = f'''
python -m lii [option]
-h, --help                 Print usage
--image-from=<str>         Specify image name. Default: '{APP_CONFIGURATION_DEF["image_from"]}'
--image-maintainer=<str>   Specify image maintainer. Default: '{APP_CONFIGURATION_DEF["image_maintainer"]}'
--name=<str>               Specify name. Default: '{APP_CONFIGURATION_DEF["name"]}'
--version=<x.x.x>          Specify version. Default: '{APP_CONFIGURATION_DEF["version"]}'
--port=<number>            Specify server port. Default: {APP_CONFIGURATION_DEF["port"]}
--localhub=<path>          Specify local hub path
--debug                    Run as debug
'''.strip()

try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "image-from=", "image-maintainer=", "name=", "version=", "port=", "debug", "localhub="])
    for name, value in opts:
        if name in ("-h", "--help"):
            print(USAGE_DEF)
            sys.exit(0)
        elif name in ("--image-from"):
            APP_CONFIGURATION_DEF.update(image_from = value)
        elif name in ("--image-maintainer"):
            APP_CONFIGURATION_DEF.update(image_maintainer = value)
        elif name in ("--name"):
            APP_CONFIGURATION_DEF.update(name = value)
        elif name in ("--version"):
            APP_CONFIGURATION_DEF.update(version = value)
        elif name in ("--port"):
            APP_CONFIGURATION_DEF.update(port = value)
        elif name in ("--debug"):
            APP_CONFIGURATION_DEF.update(isdebug = True)
        elif name in ("--localhub"):
            APP_CONFIGURATION_DEF.update(localhub = value)

    scan_module(__loader__.name.replace('__main__', "sh.installation"))

    image_prof = ImageProf(
        image_maintainer = APP_CONFIGURATION_DEF['image_maintainer'],
        image_from = APP_CONFIGURATION_DEF['image_from'],
        name = APP_CONFIGURATION_DEF['name'],
        version = APP_CONFIGURATION_DEF['version']
    )

    inst = Installer(image_prof, server_port = APP_CONFIGURATION_DEF['port'], localhub = APP_CONFIGURATION_DEF.get('localhub'))

    if APP_CONFIGURATION_DEF.get('isdebug'):
        inst.exec()
    else:
        with tempfile.TemporaryDirectory() as td:
            inst.exec(workdir = td)
except SystemExit as ex:
    if 0 != ex.code:
        traceback.print_exc()
except getopt.GetoptError as ex:
    traceback.print_exc()
    sys.exit(1)
except BaseException as e:
    # warnings.warn(e)
    traceback.print_exc()
    #info = traceback.format_exc()