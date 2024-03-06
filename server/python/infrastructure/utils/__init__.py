
import string
import secrets


def create_salt(length: int = 10) -> str:
    """
    Create a random string
    :param length: Length of the token
    :return: Return a random string
    """
    base = string.ascii_letters + string.digits
    return ''.join([secrets.choice(base) for _ in range(length)])