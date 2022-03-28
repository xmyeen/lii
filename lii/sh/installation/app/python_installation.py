#!/env/Python

from typing import IO
from urllib.parse import urlparse
from ..common import gen_download_content
from ....datatype.installation import BasicInstallation, app_d

#/root/.local/share/virtualenvs/aliblab-zGTWfjcM/lib/python3.8/site-packages/pandas/compat/__init__.py:97: UserWarning: Could not import the lzma module. Your installed Python is incomplete. Attempting to use lzma compression will result in a RuntimeError

@app_d('python')
class PythonInstallation(BasicInstallation):
    def __init__(self, *args, **kwargs):
        BasicInstallation.__init__(self, *args, **kwargs)

    def now(self, output:IO):
        installation_as_ext_cfg = self.configuration.get('ext')
        url = installation_as_ext_cfg.get('url').format(**self.configuration)
        pypi = installation_as_ext_cfg.get('pypi')
        pypi_url = urlparse(pypi)
        with gen_download_content(output, url, self.work_dir) as catalog_dir:
            output.write('\n'.join([
                f'cd {catalog_dir}/Python-*',
                f'./configure --prefix={self.home}',
                'make',
                'make install',

                'cat > /etc/pip.conf << EOF',
                '[global]',
                'timeout = 120',
                f'index-url = {pypi}',
                '[install]',
                f'trusted-host = {pypi_url.netloc}',
                'disable-pip-version-check = false',
                '[download]',
                f'trusted-host = {pypi_url.netloc}',
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
            ]))
            output.write('\n')
            self.gen_scripts_content(output, dist_dir = self.home, cfg = installation_as_ext_cfg)