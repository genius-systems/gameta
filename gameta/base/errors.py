

__all__ = ['GametaError', 'VCSError', 'CommandError', 'ContextError']


class GametaError(Exception):
    """
    Base Gameta Error from which all Gameta related errors inherit
    """


class VCSError(GametaError):
    """
    Errors related to Gameta VCS
    """


class CommandError(GametaError):
    """
    Errors related to Gameta Commands
    """


class ContextError(GametaError):
    """
    Errors related to Gameta Contexts
    """