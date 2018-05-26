#!/usr/bin/env python
from setuptools import setup

VERSION = '0.9.5'
DOWNLOAD_URL = 'https://github.com/ImSingee/PayJS/archive/v0.9.5.tar.gz'

setup(
    name='PayJS',
    version=VERSION,
    packages=['PayJS'],
    url='https://github.com/ImSingee/PayJS',
    license='MIT',
    author='Brian Wang',
    author_email='imsingee@gmail.com',
    description='An interface for payjs.cn',
    install_requires=[
        "requests>=2.18.4",
    ],
    keywords='python package payjs interface API wechat pay',
    download_url=DOWNLOAD_URL,
)
