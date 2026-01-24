import flask
from flask import session
import sqlite3
from app.config import DATABASE, app, TOKEN_TITLE


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

def get_user_id() -> int | None:
    token = session[TOKEN_TITLE]
    query_result = query_db("SELECT id FROM UserTokens WHERE token=?", (token,), True)
    print(query_result)
    response: dict = query_result["response"]
    if response == None: return None
    idx = response["id"]
    return idx

def get_permissions(userid: int) -> list[int]:
    query_result = query_db("SELECT permid FROM GrantedPermissions WHERE userid=?", (userid,))
    responses = query_result["response"]
    result: list[int] = []
    for response in responses:
        result.append(response["permid"])
    
    return result

def has_permission(userid: int, permid: int | None) -> bool:
    if permid == None: return False
    query_result = query_db("SELECT permid FROM GrantedPermissions WHERE userid=? AND permid=?", (userid, permid))
    response = query_result["response"]
    return len(response) > 0

def get_parent_permid(permid: int | None) -> int | None:
    query_result = query_db("SELECT parentpermid FROM Permissions WHERE id=?", (permid,), True)
    response: dict = query_result["response"]
    pid = response["parentpermid"]
    return pid

def is_base_permission(permid: int, checkable_permid: int) -> bool:
    if permid == checkable_permid: return True
    curpermid = permid
    while curpermid != checkable_permid:
        curpermid = get_parent_permid(curpermid)
        if curpermid == None:
            return False
    else:
        return True

def check_permission(userid: int, permid: int) -> bool:
    """Deep check of permission"""
    pid: int | None = permid
    while not has_permission(userid, pid):
        pid = get_parent_permid(pid)
        if pid == None:
            return False
    
    else:
        return True

def count_permission_depth(permid: int) -> int:
    counter = 0
    curpermid = permid
    while curpermid != None:
        curpermid = get_parent_permid(curpermid)
        counter += 1
    return counter

def grant_permission(userid: int, permid: int):
    query_db("""
        INSERT OR IGNORE INTO
            GrantedPermissions(userid, permid)
        VALUES (?, ?)""", (userid, permid))

def revoke_permission(userid: int, permid: int):
    query_db("""
        DELETE FROM
            GrantedPermissions
        WHERE userid=? AND permid=?""", (userid, permid))
