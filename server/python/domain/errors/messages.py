from ast import parse, Call
from domain.errors import *

_get_error_name = lambda code: code.split('(', 1)[0]

_MESSAGES = {
    _get_error_name(LENGTH_NOT_VALID): "field {0!s} must have a length between {1:d} and {2:d}",
    _get_error_name(PATTERN_NOT_VALID): "field {0!s} does not match pattern {1!r}",
    _get_error_name(EMPTY): "field {0!s} can not be empty or null",
    _get_error_name(EQUALS): "field {0!s} not suffer change",
    _get_error_name(INVALID_CREDENTIAL): "invalid credentials",
    _get_error_name(NOT_FOUND): "entity {0!s} with id {1!r} was not found",
}


def get_error_message(error_code: str) -> str:
    """
    Parse error codes into a human readable error message
    :param error_code: Original error code
    :return: Error message parsed
    """
    module: Call = parse(error_code).body[0].value
    if module.func.id not in _MESSAGES:
        return error_code

    values = [v.value for v in module.args]
    return _MESSAGES[module.func.id].format(*values)
