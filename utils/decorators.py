from flask import request

from auth import get_current_role


def allow_methods(allowed_methods, callback=None):
    def allow_methods_decorated(fn):
        def decorated(*args, **kwargs):
            if request.method not in allowed_methods:
                return callback() if callback else 'Method is not allowed'

            return fn(*args, **kwargs)

        decorated.__name__ = fn.__name__ + '_decorated_by_allow_methods'

        return decorated

    return allow_methods_decorated


def allow_roles(allowed_roles, callback=None):
    def allow_roles_decorated(fn):
        def decorated(*args, **kwargs):
            if get_current_role() not in allowed_roles:
                return callback() if callback else 'Page is not allowed to view'

            return fn(*args, **kwargs)

        decorated.__name__ = fn.__name__ + '_decorated_by_allow_roles'

        return decorated

    return allow_roles_decorated
