import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = "pysform",
    version = "0.1",
    description = "A library for generating and validating HTML forms",
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://pypi.python.org/pypi/pysform',
    license='BSD',
    packages=['pysform'],
    install_requires = [
        "FormEncode>=1.2",
        "WebHelpers>=0.6.4"
    ],
    zip_safe=False
)