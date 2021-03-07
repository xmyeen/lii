import os, uuid, warnings
from typing import List, str, Any
from contextlib import contextmanager
# from ...datatype.app_prof import AppProf
from ...datatype.installation import BasicInstallation
from ...en.installation import InstallationMethodDefs
from ...en.compression import CompressionDefs

@contextmanager
def gen_download_content(io:IO, url:str, work_dir:str) -> str:
    '''生成下载相关的脚本
    '''
    # if InstallationMethodDefs.http.name != installation.prof.install:
    #     return ""

    if not url:
        warnings.warn(f"No url specified")
        return ""

    io.write(f'[ -e "{work_dir}" ] && rm -f {work_dir}\n')
    io.write(f'mkdir -p {work_dir}/{{b,d}}\n')

    output_file = f"{work_dir}/d/{os.path.basename(url)}"
    if url.startswith('file://'):
        io.write(f'mv -f {url[7:]} {output_file}\n')
    elif url.startswith('http'):
        io.write(f"curl -skL -o {output_file} {url}\n")

    tmpdir = f'{work_dir}/b'
    if output_file.endswith(CompressionDefs.XZ.value):
        io.write(f"xz -d {output_file} &&\n")
        io.write(f"tar -xf {output_file[:-3]} -C {tmpdir} &&\n")
    elif output_file.endswith(CompressionDefs.GZ.value):
        io.write(f"tar -zxf {output_file} -C {tmpdir} &&\n")
    elif output_file.endswith(CompressionDefs.BZ).value:
        io.write(f"tar -jxf {output_file} -C {tmpdir} &&\n")
    elif output_file.endswith(CompressionDefs.BZ2.value):
        io.write(f"tar -jxf {output_file} -C {tmpdir} &&\n")
    elif output_file.endswith(CompressionDefs.Z):
        io.write(f"tar -Zxf {output_file} -C {tmpdir} &&\n")
    elif output_file.endswith(CompressionDefs.TAR.value):
        io.write(f"tar -xf {output_file} -C {tmpdir} &&\n")
    elif output_file.endswith(CompressionDefs.ZIP.value):
        io.write(f"unzip {output_file} -d {tmpdir} &&\n")
    
    yield tmpdir
    # elif output_file.endswith(CompressionDefs.RPM.value):
    #     io.write(f"cd {output_dir} && {{ rpm2cpio {output_file} | cpio -div }} && cd - >/dev/null")
    # if output_dir:
    #     io.write(f"find $temp_dir -maxdepth 1 -mindepth 1 -type d -execdir mv -vf {{}} {output_dir} \; &&")
    #     io.write("rm -rf $temp_dir &&")
    #     io.write("unset temp_dir &&")
    #     io.write(f"output_dir={output_dir}")
    # else:
    #     io.write(f"output_dir=\"$(find $temp_dir -maxdepth 1 -mindepth 1 -type d)\"")

    io.write(f'rm -rf {work_dir}\n')
    # lines.append(f"cd - >/dev/null")

class DnfInstallation(BasicInstallation):
    def __init__(self):
        BasicInstallation.__init__(self)

    @property
    def pkgs(self):
        pkgs = []
        if not self.configuration.get("dnf"):
            pkgs.append(self.name)
        else:
            pkgs.extend(self.configuration.get("dnf").get("pkg").split(' '))
        
        return pkgs
            
    def now(self, io:IO):
        if InstallationMethodDefs.dnf.name == self.configuration.get("install"):
            io.write('\n'.join([
                f'#--- Install {self.name}',
                f'yum install -y {"".join(self.pkgs)}'
            ]).strip())
            
            self.gen_env_content(io, self.configuration.get('dnf'))

class BinaryInstallation(BasicInstallation):
    def __init__(self):
        BasicInstallation.__init__(self)

    def now(self, io:IO):
        if InstallationMethodDefs.bin.name == self.configuration.get("install"):
            bin_cfg = self.configuration.get('bin')
            url = bin_cfg.get('url').format(**self.configuration)
            with gen_download_content(io, url, self.work_dir) as bin_dir:
                self.gen_env_content(io, self.configuration.get('dnf'))
                self.gen_scripts_content(io, dist_dir = bin_dir)
