"""
File wiht utils functions
"""


def isdeleted(obj):
    """
    Function to check if model instance is deleted
    Args:
        obj: instance os a paranoid Model
    Returns:
        bool(): if obj is soft deleted
    """
    return obj.deleted_at is not None


def all_list(iterable, key):
    """
    Method to check if all item in iterable pass the key
    Args:
        iterable: iterable with all objects
        key: function to apply on every object
    Returns:
        bool(): if all objects pass the key
    """
    return all([key(item) for item in iterable])


def any_list(iterable, key):
    """
    Method to check if all item in iterable pass the key
    Args:
        iterable: iterable with all objects
        key: function to apply on every object
    Returns:
        bool(): if any objects pass the key
    """
    return any([key(item) for item in iterable])
