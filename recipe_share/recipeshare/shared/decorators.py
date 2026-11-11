from functools import wraps

from flask import abort, session


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            abort(401)
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("user_id") is None:
                abort(401)
            if session.get("user_role") not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def owner_required(owner_id_field: str = "author_id"):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            owner_id = kwargs.get(owner_id_field)
            if owner_id is not None and session.get("user_id") != owner_id:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
