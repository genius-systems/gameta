

class GametaError(Exception):
    """
    Base Gameta Error from which all Gameta related errors inherit
    """


class VCSError(GametaError):
    """
    Errors related to Gameta VCS
    """