#!/env/Python

from ..common import insert_download_content
from ....datatype.installation import BasicAppInstallation, app_d

#/root/.local/share/virtualenvs/aliblab-zGTWfjcM/lib/python3.8/site-packages/pandas/compat/__init__.py:97: UserWarning: Could not import the lzma module. Your installed Python is incomplete. Attempting to use lzma compression will result in a RuntimeError

@app_d('python')
class PythonInstallation(BasicAppInstallation):
    def __init__(self, *args, **kwargs):
        BasicAppInstallation.__init__(self, *args, **kwargs)

    def now(self):
        lines = ['# python installation']
        with insert_download_content(lines, self) as catalog_dir:
            lines.extend([
                f'cd {catalog_dir}/Python-*',
                f'./configure --prefix={self.home}',
                'make',
                'make install',

                'cat > /etc/pip.conf << EOF',
                '[global]',
                'timeout = 120',
                'index-url = https://mirrors.aliyun.com/pypi/simple/',
                '[install]',
                'trusted-host = mirrors.aliyun.com',
                'disable-pip-version-check = false',
                '[download]',
                'trusted-host = mirrors.aliyun.com',
                'disable-pip-version-check = false',
                'EOF',

                'cat >> ${HOME}/.bashrc << EOF',
                '# python',
                f'export LD_LIBRARY_PATH={self.home}/lib:\\${{LD_LIBRARY_PATH}}',
                f'export PATH=\\${{PATH}}:{self.home}/bin',
                'EOF',

                'sh -i -l << EOF',
                'source ${HOME}/.bashrc',
                'python3 -m pip install wheel pipenv',
                'EOF',

                "cd - >/dev/null"
            ])

        return '\n'.join(lines).strip()