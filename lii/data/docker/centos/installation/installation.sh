#!/bin/sh

# yum configuration
centos_version=$(cat /etc/centos-release | cut -f4 -d' ' | cut -f'1' -d'.')
{mirror_content}
yum makecache

# language configuration
sed -i "s/override_install_langs/#override_install_langs/g" /etc/yum.conf &&
echo "export LC_ALL=zh_CN.UTF-8" >> /etc/locale.conf && 
yum install -y kde-l10n-Chinese && 
yum -q -y reinstall glibc-common && 
localedef -c -f UTF-8 -i zh_CN zh_CN.utf8

cat >> ${{HOME}}/.bashrc <<EOF
# languages
export LANG=zh_CN.UTF-8
export LANGUAGE=zh_CN:zh
export LC_ALL=zh_CN.UTF-8
EOF
source ${{HOME}}/.bashrc

# application installation
{installation_content}

# entrypint
[ -e "/docker-entrypoint" ] &&
chmod +x /docker-entrypoint

# cert
# echo -n | \\
# openssl s_client -showcerts -connect hub.docker.com:443 2>/dev/null | \\
# sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' >> /etc/ssl/certs/ca-certificates.crt
# openssl s_client -showcerts -connect hub.docker.com:443 2>/dev/null | \\
# sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /etc/ssl/certs/docker-hub-certificates.crt
# update-ca-trust

# clear
yum clean all
rm -rf /tmp/*