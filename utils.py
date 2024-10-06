import os


def to_list(value, separator=","):
    """Convert a string to a list.

    This function converts a string to a list by splitting the string
    using the specified separator. The default separator is a comma.

    Args:
        value (str): The string to convert to a list.
        separator (str): The separator to use when splitting the string.

    Returns:
        list: The list of items from the string.

    Examples:
        >>> to_list("a,b,c")
        ['a', 'b', 'c']

        >>> to_list("1,2,3", separator=",")
        ['1', '2', '3']

    """
    if isinstance(value, list):
        return value

    return value.split(separator)


def to_bool(value):
    """Convert a string to a boolean.

    This function converts a string to a boolean value. The string is
    converted to lowercase before being checked for truthy values such
    as 'true', 'yes', 'on', '1', or 't'. If the string does not match
    any of these values, the function returns False.

    Args:
        value (str): The string to convert to a boolean.

    Returns:
        bool: The boolean value of the string.

    Examples:
        >>> to_bool("true")
        True

        >>> to_bool("false")
        False

    """
    if isinstance(value, bool):
        return value

    return str(value).lower() in ["true", "yes", "on", "1", "t"]


def to_upper(value):
    """Convert a string to uppercase.

    This function converts a string to uppercase using the built-in
    `str.upper()` method.

    Args:
        value (str): The string to convert to uppercase.

    Returns:
        str: The string converted to uppercase.

    Examples:
        >>> to_upper("hello, world!")
        'HELLO, WORLD!'

    """
    return value.upper()


def getenv(name, default=None, cast=None):
    """Get an environment variable with an optional default value and cast.

    This function retrieves an environment variable by name and returns its value
    as a string. If the environment variable is not found, the default value is
    returned. An optional cast parameter can be provided to convert the value to
    a specific type, such as int or bool, or any function that accepts a single
    string argument.

    Args:
        name (str): The name of the environment variable to retrieve.
        default (str): The default value to return if the environment variable is not found.
        cast (callable): An optional function to cast the value to a specific type.

    """
    value = os.getenv(name, default)

    if cast is not None:
        value = cast(value)

    return value
