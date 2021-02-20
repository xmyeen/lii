#!/env/Python

from ..common import insert_download_content
from ....datatype.installation import BasicAppInstallation, app_d

@app_d('rust')
class RustInstallation(BasicAppInstallation):
    def __init__(self, *args, **kwargs):
        BasicAppInstallation.__init__(self, *args, **kwargs)

    def now(self):
        RUSTUP_REGISTRY = "mirrors.sjtug.sjtu.edu.cn"
        RUSTUP_REGISTRY_NAME = "utsc"

        lines =  [
            '# rust installation',

            'ENV_FILE="$HOME/.rust-env"',

            'cat >> $ENV_FILE << EOF',
            '# rust'
            f'export RUSTUP_DIST_SERVER=https://{RUSTUP_REGISTRY}/rust-static',
            f'export RUSTUP_UPDATE_ROOT=\\${{RUSTUP_DIST_SERVER}}/rustup',
            'EOF',

            'source $ENV_FILE',
            'curl https://sh.rustup.rs -sSf | sh -s -- -y',

            'cat $ENV_FILE >> ${HOME}/.bashrc',

            'cat >> $HOME/.cargo/config <<EOF',
            '[source.crates-io]',
            'registry = "https://github.com/rust-lang/crates.io-index"',
            f"replace-with = '{RUSTUP_REGISTRY_NAME}'",
            f'[source.{RUSTUP_REGISTRY_NAME}]'
            f"registry = 'git://{RUSTUP_REGISTRY}/crates.io-index'",
            'EOF',

            'rm -f $ENV_FILE',
            'unset ENV_FILE'
        ]

        return '\n'.join(lines).strip()