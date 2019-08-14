# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/14
Description:
    setup.py
----------------------------------------------------------------------------"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyeasyrpc",
    version="0.0.1",
    license='MIT',
    author='Quanyong Huang',
    author_email='quanyongh@foxmail.com',
    description="a Python RPC framework using redis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wo1fsea/PyEasyRPC",
    download_url='https://github.com/wo1fsea/PyEasyRPC/releases/tag/v0.0.1',
    keywords=['rpc-framework', 'redis'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=['msgpack-python', 'shortuuid', 'redis'],
    packages=setuptools.find_packages(),
)
