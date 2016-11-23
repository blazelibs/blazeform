from __future__ import absolute_import
import os
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()
VERSION = open(os.path.join(cdir, 'blazeform', 'version.txt')).read().strip()

setup(
    name = "BlazeForm",
    version = VERSION,
    description = "A library for generating and validating HTML forms",
    long_description=README + '\n\n' + CHANGELOG,
    author = "Randy Syring",
    author_email = "randy.syring@level12.io",
    url='http://pypi.python.org/pypi/BlazeForm',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP'
      ],
    license='BSD',
    packages=['blazeform'],
    install_requires = [
        "FormEncode>=1.2.2",
        "BlazeUtils>=0.3.0",
        "WebHelpers2"
    ],
    zip_safe=False
)
