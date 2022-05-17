from typing import Any

from naff import Permissions, slash_default_member_permission


def restrict_default_permission() -> Any:
    """
    Decorator that replaces @slash_default_member_permission()

    Call with `@restrict_default_permission()`
    """

    def wrapper(func):
        return slash_default_member_permission(permission=Permissions.ADMINISTRATOR)(func)

    return wrapper
