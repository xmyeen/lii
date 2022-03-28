#!/env/Python

from ..common import gen_download_content
from typing import IO
from ....datatype.installation import BasicInstallation, app_d

# @app_d('git')
# class GitInstallation(BasicInstallation):
#     def __init__(self, *args, **kwargs):
#         BasicInstallation.__init__(self, *args, **kwargs)

#     def after(self, output:IO):
#         return 'git config --global http.sslVerify false'