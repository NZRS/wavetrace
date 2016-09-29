from distutils.core import setup

setup(
    name='wavetrace',
    version='3.0.0',
    author='Alex Raichev',
    packages=['wavetrace', 'tests'],
    url='https://github.com/nzrs/wavetrace',
    license='LICENSE',
    description='Python 3.5 tools to produce radio signal coverage reports, mostly for New Zealand',
    long_description=open('README.rst').read(),
    install_requires=[
        'requests>=2.10.0',
        'Shapely>=1.5.16',
        'click>=6.6',
    ],
    entry_points={
        'console_scripts': ['wavey=wavetrace.cli:wavey'],
    },
)
