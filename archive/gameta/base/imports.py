from typing import Any, List

import pkg_resources

__all__ = ['import_plugins']


def import_plugins(entry_point: str) -> List[Any]:
    """
    Imports plugins specified by an entry point

    Returns:
        List[Any]: Loaded plugins
    """
    return [entry_point.load() for entry_point in pkg_resources.iter_entry_points(entry_point)]
