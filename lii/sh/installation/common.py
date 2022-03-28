import os, uuid, warnings
from typing import List, Any, IO
from contextlib import contextmanager
# from ...datatype.app_prof import AppProf
from ...datatype.installation import BasicInstallation
from ...en.installation import InstallationMethodDefs
from ...en.compression import CompressionDefs

@contextmanager
def gen_download_content(output:IO, url:str, work_dir:str) -> str:
    '''生成下载相关的脚本
    '''
    # if InstallationMethodDefs.http.name != installation.prof.install:
    #     return ""

    if not url:
        warnings.warn(f"No url specified")
        return ""

    output.write(f'[ -e "{work_dir}" ] && rm -rf {work_dir}\n')
    output.write(f'mkdir -p {work_dir}/{{b,d}}\n')

    output_file = f"{work_dir}/d/{os.path.basename(url)}"
    if url.startswith('file://'):
        output.write(f'mv -f {url[7:]} {output_file}\n')
    elif url.startswith('http'):
        output.write(f"curl -skL -o {output_file} {url}\n")

    tmpdir = f'{work_dir}/b'
    if output_file.endswith(CompressionDefs.XZ.value):
        output.write(f"xz -d {output_file}\n")
        output.write(f"tar -xf {output_file[:-3]} -C {tmpdir}\n")
    elif output_file.endswith(CompressionDefs.GZ.value):
        output.write(f"tar -zxf {output_file} -C {tmpdir}\n")
    elif output_file.endswith(CompressionDefs.BZ).value:
        output.write(f"tar -jxf {output_file} -C {tmpdir}\n")
    elif output_file.endswith(CompressionDefs.BZ2.value):
        output.write(f"tar -jxf {output_file} -C {tmpdir}\n")
    elif output_file.endswith(CompressionDefs.Z):
        output.write(f"tar -Zxf {output_file} -C {tmpdir}\n")
    elif output_file.endswith(CompressionDefs.TAR.value):
        output.write(f"tar -xf {output_file} -C {tmpdir}\n")
    elif output_file.endswith(CompressionDefs.ZIP.value):
        output.write(f"unzip {output_file} -d {tmpdir}\n")
    
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

    output.write(f'rm -rf {work_dir}\n')
    # lines.append(f"cd - >/dev/null")

class DnfInstallation(BasicInstallation):
    def __init__(self):
        BasicInstallation.__init__(self)

    @property
    def pkgs(self):
        pkg = self.configuration.get("dnf", {}).get("pkg", "").strip()
        if not pkg: return [self.name]
        return pkg.format(**self.configuration).split(' ')
            
    def now(self, output:IO):
        if InstallationMethodDefs.dnf.name == self.configuration.get("install"):
            installation_as_dnf_cfg = self.configuration.get('dnf', {})

            if self.pkgs:
                output.write(f'yum install -y {"".join(self.pkgs)}\n')
            
            self.gen_env_content(output, installation_as_dnf_cfg)
            self.gen_scripts_content(output, dist_dir = None, cfg = installation_as_dnf_cfg)

class BinaryInstallation(BasicInstallation):
    def __init__(self):
        BasicInstallation.__init__(self)

    def now(self, output:IO):
        if InstallationMethodDefs.bin.name == self.configuration.get("install"):
            installation_as_bin_cfg = self.configuration.get('bin', {})
            url = installation_as_bin_cfg.get('url').format(**self.configuration)
            with gen_download_content(output, url, self.work_dir) as catalog_dir:
                self.gen_env_content(output, installation_as_bin_cfg)
                self.gen_scripts_content(output, dist_dir = catalog_dir, cfg = installation_as_bin_cfg)
