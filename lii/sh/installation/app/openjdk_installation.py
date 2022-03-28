#!/env/Python

from ..common import gen_download_content
from ....datatype.installation import BasicInstallation, app_d

# @app_d('openjdk')
# class OpenjdkInstallation(BasicInstallation):
#     def __init__(self, *args, **kwargs):
#         BasicInstallation.__init__(self, *args, **kwargs)

#     def now(self):
#         lines =  [
#             '# openjdk installation',

#             self.gen_rpm_content(),

#             'cat >> ${HOME}/.bashrc << EOF',
#             '# openjdk',
#             f'export JAVA_HOME=/usr/lib/jvm/java-{self.prof.version}-openjdk/',
#             'export CLASSPATH=.:\\${JAVA_HOME}/lib:\\${JAVA_HOME}/lib/dt.jar:\\${JAVA_HOME}/lib/tools.jar',
#             'export PATH=\\${PATH}:\\${JAVA_HOME}/bin',
#             'EOF'
#         ]

#         return '\n'.join(lines).strip()