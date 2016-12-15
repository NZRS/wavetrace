from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='wavetrace',
    version='3.0.1',
    author='Alex Raichev',
    packages=find_packages(exclude=('tests', 'docs')),
    url='https://github.com/nzrs/wavetrace',
    license=license,
    description='Python 3.5 tools to produce radio signal coverage reports, mostly for New Zealand',
    long_description=readme,
    install_requires=[
        'requests>=2.10.0',
        'Shapely>=1.5.16',
        'click>=6.6',
    ],
    entry_points={
        'console_scripts': ['wavey=wavetrace.cli:wavey'],
    },
)
