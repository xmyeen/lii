# -*- coding:utf-8 -*-
#!/usr/bin/env Python

import os
from datetime import datetime
from setuptools import setup, find_packages

if os.path.exists("doc/README.md"):
    with open("doc/README.md", "r") as fh:
        long_description = fh.read()
else:
    long_description = ""

def get_installing_requirements():
    requirements = []

    file_path = os.path.join(os.getcwd(), 'requirements.txt' )

    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as f:
            requirements.extend([ l.strip() for l in f.readlines() ])

    return requirements

setup(
    name="lii",
    version="-".join(["1.0.0",datetime.now().strftime("%Y%m%d%H%M%S")]),
    author='xmyeen',
    author_email="xmyeen@sina.com.cn",
    url="https://github.com/xmyeen/lii",
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    platforms=["all"],
    classfiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    install_requires = get_installing_requirements(),
    py_modules = ["lii"]
)
