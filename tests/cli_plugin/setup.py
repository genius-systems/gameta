from setuptools import setup

VERSION = "0.1.0"

setup(
    name="test_cli_plugin",
    packages=["cli_plugin"],
    version=VERSION,
    install_requires=["Click"],
    entry_points={
        "gameta.cli": ["test = cli_plugin:test_cli"],
    },
)
