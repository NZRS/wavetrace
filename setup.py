from distutils.core import setup

setup(
    name='wavetrace',
    version='1.0.0',
    author='Alex Raichev',
    packages=['wavetrace', 'tests'],
    url='https://github.com/nzrs/wavetrace',
    license='LICENSE',
    description='A Python 3.4 tool kit for processing General Transit Feed Specification (GTFS) data',
    long_description=open('README.rst').read(),
    install_requires=[
        'requests>=2.10.0',
        'beautifulsoup4>=4.5.1',
    ],
)
