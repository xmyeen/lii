#!/env/Python

from ..common import insert_download_content
from ....datatype.installation import BasicAppInstallation, app_d

@app_d('maven')
class MavenInstallation(BasicAppInstallation):
    def __init__(self, *args, **kwargs):
        BasicAppInstallation.__init__(self, *args, **kwargs)

    def now(self):
        lines =  [
            '# maven installation',

            self.gen_rpm_content(),

            'cat >> ${HOME}/.bashrc << EOF',
            '# maven',
            'EOF'
        ]

        return '\n'.join(lines).strip()