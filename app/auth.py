import flask
import sqlite3
from app.config import DATABASE, app


class Validator:
    @staticmethod
    def passwords(password: str, password_confirmation: str) -> bool:
        return password == password_confirmation
    @staticmethod
    def username_pattern(username: str, pattern: str) -> bool:
        return not username.find(pattern) >= 0
    @staticmethod
    def username(username: str) -> bool:
        return any([
            Validator.username_pattern(username, " "),
            Validator.username_pattern(username, "\t"),
            Validator.username_pattern(username, "\n"),
            Validator.username_pattern(username, "-"),
            Validator.username_pattern(username, "'"),
            Validator.username_pattern(username, "\""),
            Validator.username_pattern(username, "|"),
            Validator.username_pattern(username, "/"),
            Validator.username_pattern(username, "\\"),
        ]) or len(username) < 3

    @staticmethod
    def email(mail: str) -> bool:
        if mail.count("@") > 1 or mail.count("@") == 0: return False
        name, domain = mail.split("@")
        if name.count("+") > 0: return False
        if domain.count("+") > 0: return False
        return True

def get_db():
    db = getattr(flask.g, "_database", None)
    if db is None:
        db = flask.g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query: str, args: tuple=(), one: bool=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    rowid = cur.lastrowid
    get_db().commit()
    cur.close()
    return {
        "response": (rv[0] if rv else None) if one else rv,
        "id": rowid
    }

@app.teardown_appcontext
def close_connection(_exception):
    db: sqlite3.Connection | None = getattr(flask.g, "_database", None)
    if db is None: return
    db.close()