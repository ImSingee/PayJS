#!/usr/bin/env python
from setuptools import setup

VERSION = '1.2.2'
DOWNLOAD_URL = 'https://github.com/ImSingee/PayJS/archive/v{}.tar.gz'.format(VERSION)

setup(
    name='payjs',
    version=VERSION,
    packages=['payjs'],
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
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ]
)
