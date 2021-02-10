
from setuptools import setup

VERSION = '0.1.0'

setup(
    name='test',
    packages=['test'],
    version=VERSION,
    install_requires=[
        'Click'
    ],
    entry_points={
        'gameta.cli': [
            'test = test:test_cli'
        ],
    }
)
