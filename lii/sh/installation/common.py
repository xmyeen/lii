import os, uuid, warnings
from typing import List
from contextlib import contextmanager
from ...datatype.app_prof import AppProf
from ...datatype.installation import BasicAppInstallation
from ...en.installation import InstallationMethodDefs
from ...en.compression import CompressionDefs

@contextmanager
def insert_download_content(lines:List[str], installation:BasicAppInstallation) -> str:
    '''生成下载相关的脚本
    '''
    if InstallationMethodDefs.http.name != installation.prof.install:
        return ""

    url = installation.prof.extension.get('url')
    if not url:
        warnings.warn(f"No url specified for {installation.prof.name}")
        return ""

    lines.append(f'[ -e "{installation.building_work_dir}" ] && rm -f {installation.building_work_dir}')
    lines.append(f'mkdir -p {installation.building_work_dir}/{{b,d}}')

    output_file = f"{installation.building_work_dir}/d/{os.path.basename(url)}"
    if url.startswith('file://'):
        lines.append(f'mv -f {url[7:]} {output_file}')
    elif url.startswith('http'):
        lines.append(f"curl -skL -o {output_file} {url}")

    tmpdir = f'{installation.building_work_dir}/b'
    if output_file.endswith(CompressionDefs.XZ.value):
        lines.append(f"xz -d {output_file} &&")
        lines.append(f"tar -xf {output_file[:-3]} -C {tmpdir} &&")
    elif output_file.endswith(CompressionDefs.GZ.value):
        lines.append(f"tar -zxf {output_file} -C {tmpdir} &&")
    elif output_file.endswith(CompressionDefs.BZ).value:
        lines.append(f"tar -jxf {output_file} -C {tmpdir} &&")
    elif output_file.endswith(CompressionDefs.BZ2.value):
        lines.append(f"tar -jxf {output_file} -C {tmpdir} &&")
    elif output_file.endswith(CompressionDefs.Z):
        lines.append(f"tar -Zxf {output_file} -C {tmpdir} &&")
    elif output_file.endswith(CompressionDefs.TAR.value):
        lines.append(f"tar -xf {output_file} -C {tmpdir} &&")
    elif output_file.endswith(CompressionDefs.ZIP.value):
        lines.append(f"unzip {output_file} -d {tmpdir} &&")
    
    yield tmpdir
    # elif output_file.endswith(CompressionDefs.RPM.value):
    #     lines.append(f"cd {output_dir} && {{ rpm2cpio {output_file} | cpio -div }} && cd - >/dev/null")
    # if output_dir:
    #     lines.append(f"find $temp_dir -maxdepth 1 -mindepth 1 -type d -execdir mv -vf {{}} {output_dir} \; &&")
    #     lines.append("rm -rf $temp_dir &&")
    #     lines.append("unset temp_dir &&")
    #     lines.append(f"output_dir={output_dir}")
    # else:
    #     lines.append(f"output_dir=\"$(find $temp_dir -maxdepth 1 -mindepth 1 -type d)\"")

    lines.append(f'rm -rf {installation.building_work_dir}')
    # lines.append(f"cd - >/dev/null")