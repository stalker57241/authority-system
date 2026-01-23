from app.config import app, SCHEMAS_DIR, INITIAL_SCHEMA
from app.auth import get_db, query_db

import functools

NO_PERM = None

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(f'{SCHEMAS_DIR}/{INITIAL_SCHEMA}', mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()

# def no_perm()

def require_perm(fn):
    functools.wraps(fn)
    def wrapper(perm_name: str):
        result = fn()

        return result
    return wrapper