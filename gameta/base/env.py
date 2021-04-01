from os import getenv, environ
from typing import Dict


__all__ = ['SHELL', 'ENV_VARS']


SHELL: str = getenv('SHELL', '/bin/sh')


ENV_VARS: Dict[str, str] = {
    '$' + k.upper(): v
    for k, v in environ.items()
}
