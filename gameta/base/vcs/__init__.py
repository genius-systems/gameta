from importlib import import_module
from pkgutil import iter_modules
from typing import Dict, Type

from .vcs import VCS, GametaRepo

from gameta.base.imports import import_plugins


__all__ = ['vcs_interfaces', 'VCS', 'GametaRepo']


vcs_interfaces: Dict[str, Type[VCS]] = {
    v.name: v
    for mod in [
        import_module('.'.join([__name__, i.name]))
        for i in iter_modules([__path__[0]])
        if i.name not in ['vcs']
    ]
    for v in map(mod.__dict__.get, getattr(mod, '__all__'))
    if issubclass(v, VCS)
}
vcs_interfaces.update({i.name: i for i in import_plugins('gameta.vcs')})
