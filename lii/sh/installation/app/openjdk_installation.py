#!/env/Python

from ..common import insert_download_content
from ....datatype.installation import BasicAppInstallation, app_d

@app_d('openjdk')
class OpenjdkInstallation(BasicAppInstallation):
    def __init__(self, *args, **kwargs):
        BasicAppInstallation.__init__(self, *args, **kwargs)

    def now(self):
        lines =  [
            '# openjdk installation',

            self.gen_rpm_content(),

            'cat >> ${HOME}/.bashrc << EOF',
            '# openjdk',
            f'export JAVA_HOME=/usr/lib/jvm/java-{self.prof.version}-openjdk/',
            'export CLASSPATH=.:\\${JAVA_HOME}/lib:\\${JAVA_HOME}/lib/dt.jar:\\${JAVA_HOME}/lib/tools.jar',
            'export PATH=\\${PATH}:\\${JAVA_HOME}/bin',
            'EOF'
        ]

        return '\n'.join(lines).strip()