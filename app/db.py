from app import config
from app.auth import get_db, query_db
from app import auth
from typing import Callable, Optional, Any

import flask
import functools

NO_PERM: Optional[Callable[..., Any]] = None

def init_db():
    with config.app.app_context():
        db = get_db()
        with config.app.open_resource(f'{config.SCHEMAS_DIR}/{config.INITIAL_SCHEMA}', mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()

# def no_perm()

def require_perm(perm_id):
    """ Decorator
        Usage:
        from app import config
        from app.config import app
        from app import db

        @db.require_perm(config.REPOSITORIES_PERMID)
        @app.route("/resositories")
        def repositories():
            return "Repositories page"
    """
    print("Require perm")
    def decorator(fn):
        print("Require perm>decorator")
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            print("Require perm>decorator>wrapper")
            user_id = auth.get_user_id()
            print(f"user_id: {user_id}")
            if user_id == None:
                if not auth.is_base_permission(perm_id, config.GUEST_PERMID):
                    return _call_no_perm(401, *args, **kwargs)
                print("Guest permission")
            else:
                if not auth.check_permission(user_id, perm_id):
                    return _call_no_perm(403, *args, **kwargs)
                print("Check completed")
            print("Access granted")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def _call_no_perm(status: int = 403, *args, **kwargs):
    if NO_PERM is None:
        return flask.abort(status)
    if callable(NO_PERM):
        return NO_PERM(*args, **kwargs)
    return NO_PERM

def no_perm(fn):
    global NO_PERM
    NO_PERM = fn
    return fn

