from typing import Any, List

import pkg_resources

from click import Group


__all__ = ['import_plugins', 'import_gameta_plugins']


def import_plugins(entry_point: str) -> List[Any]:
    """
    Imports plugins specified by an entry point

    Returns:
        List[Any]: Loaded plugins
    """
    return [entry_point.load() for entry_point in pkg_resources.iter_entry_points(entry_point)]


def import_gameta_plugins(cli: Group) -> Group:
    """
    Imports the command line interfaces of all Gameta plugins into the system

    Args:
        cli (click.Group): Gameta command line interface

    Returns:
        click.Group: Gameta command line interface with plugin interfaces attached
    """
    for entry_point in pkg_resources.iter_entry_points('gameta.cli'):
        cli.add_command(cmd=entry_point.load())

    return cli
