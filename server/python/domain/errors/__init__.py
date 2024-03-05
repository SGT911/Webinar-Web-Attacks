"""
Error codes definitions and descriptions
"""

LENGTH_NOT_VALID = "EV001({field!r},{min!r},{max!r})"
PATTERN_NOT_VALID = "EV002({field!r},{pattern!r})"
EMPTY = "EV003({field!r})"
EQUALS = "EV004({field!r})"
INVALID_CREDENTIAL = "EA001()"
PASSWORD_NOT_MATCH = "EA002()"
NOT_FOUND = "EM001({model!r},{id!r})"
ALREADY_EXISTS = "EM002({model!r},{id!r})"
