from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='wavetrace',
    version='4.0.3',
    author='Alex Raichev',
    packages=find_packages(exclude=('tests', 'docs')),
    url='https://github.com/nzrs/wavetrace',
    license=license,
    data_files = [('', ['LICENSE.txt'])],
    description='Python 3.5 tools to produce radio signal coverage reports, mostly for New Zealand',
    long_description=readme,
    install_requires=[
        'requests>=2.20.0',
        'Shapely>=1.6.4.post2',
        'click>=7.0',
    ],
    entry_points={
        'console_scripts': ['wavey=wavetrace.cli:wavey'],
    },
)
