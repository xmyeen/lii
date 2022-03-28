#!/env/Python

from ..common import gen_download_content
from ....datatype.installation import BasicInstallation, app_d

# @app_d('maven')
# class MavenInstallation(BasicInstallation):
#     def __init__(self, *args, **kwargs):
#         BasicInstallation.__init__(self, *args, **kwargs)

#     def now(self):
#         lines =  [
#             '# maven installation',

#             self.gen_rpm_content(),

#             'cat >> ${HOME}/.bashrc << EOF',
#             '# maven',
#             'EOF'
#         ]

#         return '\n'.join(lines).strip()