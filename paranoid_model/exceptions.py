"""
File with all exceptions used on Paranoid Model
"""


class SoftDeleted(Exception):
    """Object has been soft deleted."""
    pass


class IsNotSoftDeleted(Exception):
    """Object has not been soft deleted."""
    pass
