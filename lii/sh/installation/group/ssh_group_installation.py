#!/env/Python

from typing import IO
from ..common import gen_download_content
from ....datatype.installation import BasicGroupInstallation, group_d

AFTER_CONTENT_DEF = f'''
#--- enable sshd
systemctl enable sshd.service
#--- ssh configuration
mkdir -p /var/run/sshd
echo "root:abc123" | chpasswd
ssh-keygen -q -t rsa -b 2048 -f /etc/ssh/ssh_host_rsa_key -N ''
ssh-keygen -q -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''
ssh-keygen -t dsa -f /etc/ssh/ssh_host_ed25519_key  -N ''
# sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
sed -i /etc/ssh/sshd_config \\
    -e 's/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g' \\
    -e 's/UsePAM.*/UsePAM no/g' \\
    -e 's/#UsePAM no/UsePAM no/g' \\
    -e 's~^PasswordAuthentication yes~PasswordAuthentication yes~g' \\
    -e 's~^#PermitRootLogin yes~PermitRootLogin yes~g' \\
    -e 's~^#UseDNS yes~UseDNS no~g' \\
    -e 's~^\\(.*\\)/usr/libexec/openssh/sftp-server$~\\1internal-sftp~g'
'''.strip()

@group_d('ssh')
class SshGroupInstallation(BasicGroupInstallation):
    def __init__(self):
        BasicGroupInstallation.__init__(self)
        
    def after(self, output:IO) -> str:
        output.write(AFTER_CONTENT_DEF.strip())
        output.write('\n')