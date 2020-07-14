import os
from setuptools import setup, find_packages

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

version_fpath = os.path.join(cdir, 'blazeform', 'version.py')
version_globals = {}
with open(version_fpath) as fo:
    exec(fo.read(), version_globals)

setup(
    name="BlazeForm",
    version=version_globals['VERSION'],
    description="A library for generating and validating HTML forms",
    long_description='\n\n'.join((README, CHANGELOG)),
    long_description_content_type='text/x-rst',
    author="Randy Syring",
    author_email="randy.syring@level12.io",
    url='https://github.com/blazelibs/blazeform',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP'
      ],
    license='BSD',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    install_requires=[
        "FormEncode>=1.3.1",
        "BlazeUtils>=0.6.2",
        "WebHelpers2"
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': [
            'codecov',
            'coverage',
            'dnspython',
            'flake8',
            'nose',
            'tox',
            'wheel',
        ],
    },
    zip_safe=False
)
