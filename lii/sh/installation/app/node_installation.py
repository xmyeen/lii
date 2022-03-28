#!/env/Python

from ..common import gen_download_content
from ....datatype.installation import BasicInstallation, app_d

# @app_d('node')
# class NodeInstallation(BasicInstallation):
#     def __init__(self, *args, **kwargs):
#         BasicInstallation.__init__(self, *args, **kwargs)

#     def now(self):
#         lines = ['# node installation']
#         with gen_download_content(lines, self) as catalog_dir:
#             lines.extend([
#             f'mv -f {catalog_dir}/node-*-linux-* {self.home}',

#             'cat >> ${HOME}/.bashrc << EOF',
#             '# node',
#             f'export LD_LIBRARY_PATH={self.home}/lib:\\${{LD_LIBRARY_PATH}}',
#             f'export PATH=\\${{PATH}}:{self.home}/bin',
#             'EOF'
#             ])

#         return '\n'.join(lines).strip()