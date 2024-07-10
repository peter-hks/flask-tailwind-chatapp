"""admin_required.py"""

from functools import wraps
from typing import TYPE_CHECKING, Callable

from flask import flash, redirect, url_for
from flask_login import current_user

# from orms.user import User
if TYPE_CHECKING:
    from orms.user import User

    current_user: User


def admin_required(_func: Callable):
    """Decorator to require admin privileges to access a route.

    Args:
        - _func (Callable): The function to decorate.\n
    Returns:
        Callable: The decorated function.
    """

    @wraps(_func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        if not current_user.is_admin:
            flash("You do not have permission to view this page.", "danger")
            return redirect(url_for("chat"))  # redirect users without admin privileges
        return _func(*args, **kwargs)

    return decorated_function
