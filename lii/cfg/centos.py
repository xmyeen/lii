from ..en.installation import InstallationMethodDefs

CENTOS_CONFIGURATION_DFLT_DEF = {
"7": '\n'.join([
#基本组
f'''
[vim]
group = basic
install = {InstallationMethodDefs.yum.name}

[unzip]
group = basic
install = {InstallationMethodDefs.yum.name}

[bzip2]
group = basic
install = {InstallationMethodDefs.yum.name}
rpms = {{name}} {{name}}-devel

[rpm-build]
group = basic
install = {InstallationMethodDefs.yum.name}
''',

#ssh组
f'''
[openssh]
group = ssh
install = {InstallationMethodDefs.yum.name}

[openssh-server]
group = ssh
install = {InstallationMethodDefs.yum.name}

[openssh-client]
group = ssh
install = {InstallationMethodDefs.yum.name}
''',

#网络组
f'''
[iproute]
group = network
install = {InstallationMethodDefs.yum.name}

[NetworkManager]
group = network
install = {InstallationMethodDefs.yum.name}
''',

#版本控制组
f'''
[git]
group = cvs
install = {InstallationMethodDefs.yum.name}

[svn]
group = cvs
install = {InstallationMethodDefs.yum.name}
''',

#cpp开发组
f'''
[gcc]
group = cpp-devel
install = {InstallationMethodDefs.yum.name}

[gcc-c++]
group = cpp-devel
install = {InstallationMethodDefs.yum.name}

[make]
group = cpp-devel
install = {InstallationMethodDefs.yum.name}

[glibc]
group = cpp-devel
install = {InstallationMethodDefs.yum.name}

[cmake]
group = cpp-devel
install = {InstallationMethodDefs.http.name}
version = 3.15.2
url =  https://github.com/Kitware/CMake/releases/download/v{{version}}/cmake-{{version}}-Linux-x86_64.tar.gz
''',

#python开发组
f'''
[zlib]
group = python-devel
install = {InstallationMethodDefs.yum.name}

[lzma]
group = python-devel
install = {InstallationMethodDefs.yum.name}

[xz]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[openssl]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[ncurses]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[sqlite]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[readline]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[gdbm]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[tk]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[libffi]
group = python-devel
install = {InstallationMethodDefs.yum.name}
rpms = {{name}}-devel

[python]
group = python-devel
install = {InstallationMethodDefs.http.name}
version = 3.8.2
url =  https://www.python.org/ftp/python/{{version}}/Python-{{version}}.tar.xz
''',

#javascript开发组
f'''
[node]
group = javascript-devel
install = {InstallationMethodDefs.http.name}
version = 10.1.0
url =  https://nodejs.org/dist/v{{version}}/node-v{{version}}-linux-x64.tar.xz
''',

#rust开发组
f'''
[rust]
group = rust-devel
install = {InstallationMethodDefs.custom.name}
version = latest
''',

#golang开发组
f'''
[golang]
group = golang-devel
install = {InstallationMethodDefs.http.name}
version = 1.14
url =  https://mirrors.ustc.edu.cn/golang/go{{version}}.linux-amd64.tar.gz
''',

#java开发组
f'''
[openjdk]
group = java-devel
install = {InstallationMethodDefs.yum.name}
version = 11
rpms =  java-{{version}}-{{name}} java-{{version}}-{{name}}-devel

[maven]
group = java-devel
install = {InstallationMethodDefs.yum.name}
''',

#小工具组
f'''
[fvs]
group = toolkit
install = {InstallationMethodDefs.rpm.name}
version = 1.0.0
rpms =  https://github.com/xmyeen/fvs/releases/download/{{version}}-beta.3/fvs-{{version}}-1.el7.noarch.rpm
'''
])
}


CENTOS_DOCKER_TEMPALTE_DEF = {
"7": '''
FROM {image_from}

MAINTAINER {image_maintainer}

ENV LANG="zh_CN.UTF-8" LC_ALL="zh_CN.UTF-8" LANGUAGE="zh_CN:zh"

LABEL description="多开发语言统一构建环境"

RUN \\
    # 将编译时间加入登录提示
    echo "{image_name} - built in `date "+%Y%m%dT%H%M%S%z"`" >> /etc/motd; \\
    # 将环境变量写到/etc/profile里面，保证SSH登录的时候能够正确使用
    # 设置systemd可执行
    (cd /lib/systemd/system/sysinit.target.wants/; \\
    for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \\
    rm -f /lib/systemd/system/multi-user.target.wants/*; \\
    rm -f /etc/systemd/system/*.wants/*; \\
    rm -f /lib/systemd/system/local-fs.target.wants/*; \\
    rm -f /lib/systemd/system/sockets.target.wants/*udev*; \\
    rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \\
    rm -f /lib/systemd/system/basic.target.wants/*; \\
    rm -f /lib/systemd/system/anaconda.target.wants/*; \\
    # 执行安装脚本
    curl -ssL http://{http_server_addr}:{http_server_port}/{installation_file} | sh; \\
    # 安装启动脚本
    #dirname {entrypoint_script_path} | xargs mkdir -p; \\
    #basename {entrypoint_script_path} | xargs -i curl -ssL -o {entrypoint_script_path} http://{http_server_port}:{http_server_port}/{{}} | sh; \\
    #chmod 755 {entrypoint_script_path}; \\
    ls -l {entrypoint_script_path}
    

EXPOSE 22 80 8080

VOLUME [ "/sys/fs/cgroup" ]

CMD ["{entrypoint_script_path}"]
# CMD ["/usr/sbin/sshd -D"]
# CMD ["/usr/sbin/init"]
'''
}


CENTOS_INSTALLATION_TEMPALTE_DEF = {
"7": '''
#!/bin/sh

# yum configuration
centos_version=$(cat /etc/centos-release | cut -f4 -d' ' | cut -f'1' -d'.')
echo "--- Add aliyun repository"
curl -k -s -L -o /etc/yum.repos.d/aliyun.repo https://mirrors.aliyun.com/repo/Centos-${{centos_version}}.repo
sed -i -e '/mirrors.cloud.aliyuncs.com/d' -e '/mirrors.aliyuncs.com/d' /etc/yum.repos.d/aliyun.repo
echo "--- Add netease repository"
curl -k -s -L -o /etc/yum.repos.d/netease.repo https://mirrors.163.com/.help/CentOS${{centos_version}}-Base-163.repo
yum makecache

# language configuration
echo "export LC_ALL=zh_CN.UTF-8"  >> /etc/locale.conf && 
yum install -y kde-l10n-Chinese && 
yum -y reinstall glibc-common && 
localedef -c -f UTF-8 -i zh_CN zh_CN.utf8

cat >> ${{HOME}}/.bashrc <<EOF
# languages
export LANG=zh_CN.UTF-8
export LANGUAGE=zh_CN:zh
export LC_ALL=zh_CN.UTF-8
EOF
source ${{HOME}}/.bashrc

# application installation
{application_installation_content}

# entrypint
cat >> {entrypoint_script_path} << EOF
#!/bin/sh
cat /etc/motd
systemctl enable sshd.service
exec /usr/sbin/init
EOF
chmod +x {entrypoint_script_path}

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

# finish
echo "finish"
'''
}