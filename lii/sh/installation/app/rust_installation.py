#!/env/Python

from typing import IO
from ..common import gen_download_content
from ....datatype.installation import BasicInstallation, app_d

@app_d('rust')
class RustInstallation(BasicInstallation):
    def __init__(self, *args, **kwargs):
        BasicInstallation.__init__(self, *args, **kwargs)

    def now(self, output:IO):
        RUSTUP_REGISTRY = self.configuration.get("env", {}).get('RUSTUP_REGISTRY')
        RUSTUP_REGISTRY_NAME = self.configuration.get("env", {}).get('RUSTUP_REGISTRY_NAME')

        output.write('\n'.join([
            '# rust installation',

            'cat >> ${HOME}/.bashrc << EOF',
            '# rust',
            f'export RUSTUP_DIST_SERVER=https://{RUSTUP_REGISTRY}/rust-static',
            f'export RUSTUP_UPDATE_ROOT=https://{RUSTUP_REGISTRY}/rust-static/rustup',
            'EOF',

            'source ${HOME}/.bashrc',
            'curl https://sh.rustup.rs -sSf | sh -s -- -y',

            'cat > ${HOME}/.cargo/config << EOF',
            '[source.crates-io]',
            'registry = "https://github.com/rust-lang/crates.io-index"',
            f"replace-with = '{RUSTUP_REGISTRY_NAME}'",
            f'[source.{RUSTUP_REGISTRY_NAME}]',
            f"registry = 'git://{RUSTUP_REGISTRY}/crates.io-index'",
            'EOF'
        ]))
        output.write('\n')