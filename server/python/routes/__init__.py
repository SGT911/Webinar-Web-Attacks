from functools import wraps
from typing import Callable

from flask import session, redirect, url_for


def ensure_session(fx: Callable) -> Callable:
    """
    Ensure if the session is already initialized
    :param fx: Route to decorate
    :return: Wrapped route
    """
    @wraps(fx)
    def wrapper(*args, **kwargs):
        if 'session_id' not in session:
            return redirect(url_for('home'))

        return fx(*args, **kwargs)

    return wrapper
