#!/env/Python

from typing import IO
from ..common import gen_download_content
from ....datatype.installation import BasicGroupInstallation, group_d

AFTER_CONTENT_DEF = f'''
#--- restart network
systemctl enable NetworkManager
'''

@group_d('network')
class NetworkGroupInstallation(BasicGroupInstallation):
    def __init__(self):
        BasicGroupInstallation.__init__(self)

    def after(self, output:IO) -> str:
        output.write(AFTER_CONTENT_DEF.strip())
        output.write('\n')