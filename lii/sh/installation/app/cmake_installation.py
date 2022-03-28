#!/env/Python

from ..common import gen_download_content
from typing import IO
from ....datatype.installation import BasicInstallation, app_d

# @app_d('cmake')
# class CMakeInstallation(BasicInstallation):
#     def __init__(self, *args, **kwargs):
#         BasicInstallation.__init__(self, *args, **kwargs)

#     def now(self, io:IO):
#         lines = ['# cmake installation']
#         with gen_download_content(lines, self) as catalog_dir:
#             lines.extend([
#             f'mv -f {catalog_dir}/cmake-*-Linux-* {self.home}',

#             'cat >> ${HOME}/.bashrc << EOF',

#             '# cmake',
#             f'export LD_LIBRARY_PATH={self.home}/lib:\\${{LD_LIBRARY_PATH}}',
#             f'export PATH=\\${{PATH}}:{self.home}/bin',
#             'EOF'
#             ])

#         return '\n'.join(lines).strip()