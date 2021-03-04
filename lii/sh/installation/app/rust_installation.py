#!/env/Python

from ..common import insert_download_content
from ....datatype.installation import BasicAppInstallation, app_d

@app_d('rust')
class RustInstallation(BasicAppInstallation):
    def __init__(self, *args, **kwargs):
        BasicAppInstallation.__init__(self, *args, **kwargs)

    def now(self):
        RUSTUP_REGISTRY = "mirrors.ustc.edu.cn"
        RUSTUP_REGISTRY_NAME = "utsc"

        lines =  [
            '# rust installation',

            'cat >> ${HOME}/.bashrc << EOF',
            '# rust',
            f'export RUSTUP_DIST_SERVER=https://{RUSTUP_REGISTRY}/rust-static',
            f'export RUSTUP_UPDATE_ROOT=https://{RUSTUP_REGISTRY}/rust-static/rustup',
            'EOF',

            'source ${HOME}/.bashrc',
            'curl https://sh.rustup.rs -sSf | sh -s -- -y',

            'cat >> ${HOME}/.cargo/config << EOF',
            '[source.crates-io]',
            'registry = "https://github.com/rust-lang/crates.io-index"',
            f"replace-with = '{RUSTUP_REGISTRY_NAME}'",
            f'[source.{RUSTUP_REGISTRY_NAME}]',
            f"registry = 'git://{RUSTUP_REGISTRY}/crates.io-index'",
            'EOF'
        ]

        return '\n'.join(lines).strip()