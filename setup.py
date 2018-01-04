import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup


def read(fname):
    """
    定义一个read方法，用来读取目录下的长描述
    我们一般是将README文件中的内容读取出来作为长描述，这个会在PyPI中你这个包的页面上展现出来，
    你也可以不用这个方法，自己手动写内容即可，
    PyPI上支持.rst格式的文件。暂不支持.md格式的文件，.rst文件PyPI会自动把它转为HTML形式显示在你包的信息页面上。
    """
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "PayJS"

PACKAGES = ["PayJS", ]

DESCRIPTION = "A interface for payjs.cn"

LONG_DESCRIPTION = read("README.txt")

KEYWORDS = "python package payjs interface API wechat pay"

AUTHOR = "Brian Wang"

AUTHOR_EMAIL = "imsingee@gmail.com"

URL = "https://github.com/ImSingee/PayJS"
DOWNLOAD_URL = "https://github.com/ImSingee/PayJS/archive/0.9.2.tar.gz"

VERSION = "0.9.2"

LICENSE = "MIT"

INSTALL_REQUIRES = [
    "requests>=2.18.4",
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
)
