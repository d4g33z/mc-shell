from setuptools import setup, find_packages

# see https://stackoverflow.com/questions/27664504/how-to-add-package-data-recursively-in-python-setup-py
import os
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('mcshell/data')

setup(
    name='mcshell',
    version='0.1',
    packages=find_packages(include=['mcshell'],exclude=['tests','tests.*']),
    include_package_data=True,
    install_requires=[
        'rcon',
        'aio-mc-rcon',
        'ipython',
        'pickleshare', # for %store
        'urlpath',
        'rich',
        'Click',
    ],
    entry_points = {
        'console_scripts':[
            'mcshell = mcshell.mcshell:cli',
        ],
    },
    package_data={'': extra_files},
)
