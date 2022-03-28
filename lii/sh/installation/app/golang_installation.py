#!/env/Python

from ..common import gen_download_content
from ....datatype.installation import BasicInstallation, app_d

# @app_d('golang')
# class GolangInstallation(BasicInstallation):
#     def __init__(self, *args, **kwargs):
#         BasicInstallation.__init__(self, *args, **kwargs)

#     def now(self):
#         lines = ['# golang installation']
#         with gen_download_content(lines, self) as catalog_dir:
#             lines.extend([
#             f'mv -f {catalog_dir}/go {self.home}',

#             'GO_WORKSPACE=${HOME}/gowork',
#             'mkdir -p ${GO_WORKSPACE}',

#             'cat >> ${HOME}/.bashrc << EOF',
#             '# golang',
#             'export GOPATH=${GO_WORKSPACE}',
#             f'export PATH=\\${{PATH}}:{self.home}/bin',
#             'EOF',

#             'unset GO_WORKSPACE'
#             ])

#         return '\n'.join(lines).strip()