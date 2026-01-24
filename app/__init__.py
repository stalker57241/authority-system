from flask import request, session
import flask
import app.auth as auth
import hashlib
from app.config import *
from app import db, wrappers

import time

db.init_db()

@app.route("/")
def index():
    return wrappers.render_template("index.html")

@app.route("/users/<username>")
def userpage(username: str):
    email: str = auth.query_db("SELECT email FROM Users WHERE username=?", (username,), True)["response"]["email"]
    return wrappers.render_template("users/user.html", user={"username": username, "email": email})

@app.route("/users")
def users():
    query_result = auth.query_db("SELECT username FROM Users WHERE isactive=TRUE;")
    response = query_result["response"]
    userlist: list[dict[str, str]] = []
    for user in response:
        userlist.append({"name": user["username"]})
    return wrappers.render_template(
        "users/index.html", users=userlist
    )

@app.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        resp = auth.query_db("SELECT id, username FROM Users WHERE email=? AND password=?", (email, password), True)["response"]
        if resp == None or len(resp) == 0: return flask.abort(403)
        idx = resp["id"]
        username = resp["username"]
        answer = flask.make_response(
            flask.redirect(f"/users/{username}"))
        expire_secs = time.time() + 60 * 60 * 24 # Secs -> minutes -> hours -> day
        token = hashlib.sha256()
        token.update(username.encode())
        token.update(f"{expire_secs}".encode())
        
        register_token(idx, token.hexdigest(), expire_secs)

        session[USERNAME_TITLE] = username
        session[TOKEN_TITLE] = token.hexdigest()
        
        return answer
    else:
        return wrappers.render_template("auth/login.html")

@app.route("/auth/logout")
def logout():
    resp = flask.make_response(
        flask.redirect("/")
    )

    token = session[TOKEN_TITLE]
    auth.query_db("DELETE FROM UserTokens WHERE token=?", (token,), True)
    session[USERNAME_TITLE] = None
    session[TOKEN_TITLE] = None
    return resp

@app.route("/auth/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        confirm_password = hashlib.sha256(request.form['confirm_password'].encode()).hexdigest()
        if not auth.Validator.passwords(password, confirm_password): return flask.abort(422)
        print("cmp successful")
        if not auth.Validator.username(request.form['username']):    return flask.abort(422)
        print("username successful")
        if not auth.Validator.email(request.form['email']):          return flask.abort(422)
        print("email successful")
        email = request.form['email']
        print('POST', request.form)
        idx = register_user(request.form['username'], email, password)

        expire_secs = time.time() + 60 * 60 * 24 # Secs -> minutes -> hours -> day
        token = hashlib.sha256()
        token.update(request.form["username"].encode())
        token.update(f"{expire_secs}".encode())
        
        register_token(idx, token.hexdigest(), expire_secs)

        resp = flask.make_response(
            wrappers.render_template("auth/registration_successful.html", username=request.form["username"])
        )

        session["username"] = request.form["username"]
        session["token"] = token.hexdigest()

        return resp
    elif request.method == "GET":
        return wrappers.render_template("auth/register.html")
    return flask.abort(400, "Method not implemented")
    

def register_user(username: str, email: str, password_hash: str):
    
    data = auth.query_db(
        f"INSERT INTO {USER_TABLE} (username, email, password) VALUES (?, ?, ?)",
        (username, email, password_hash))
    print(data)
    return data['id']

def register_token(idx: int, token: str, expire_time):
    auth.query_db(
        f"INSERT INTO {USER_TOKEN_TABLE} (id, token, expired) VALUES (?, ?, ?)", (idx, token, expire_time)
    )

@app.route("/users/change_password", methods=["POST", "GET"])
def change_password():
    match request.method:
        case "POST":
            old_password = hashlib.sha256(request.form['old_password'].encode()).hexdigest()
            new_password = hashlib.sha256(request.form['new_password'].encode()).hexdigest()
            confirm_password = hashlib.sha256(request.form['confirm_password'].encode()).hexdigest()
            if len(auth.query_db("SELECT * FROM Users WHERE username=? AND password=?", (
                session[USERNAME_TITLE], old_password
            ), True)["response"]) == 0: return flask.abort(403)
            if not auth.Validator.passwords(new_password, confirm_password): flask.redirect("/", 422)
            resp = auth.query_db("SELECT id, expired FROM UserTokens WHERE token=?", (session[TOKEN_TITLE],), True)["response"]
            if int(resp["expired"]) < time.time():
                auth.query_db("DELETE FROM UserTokens WHERE token=?", (session[TOKEN_TITLE],))
                return flask.abort(403)
            idx = resp["idx"]
            auth.query_db("UPDATE Users SET password=? WHERE id=?", (new_password, idx))
            resp = flask.make_response(wrappers.render_template("auth/password_changed.html"))
            resp.delete_cookie("username")
            resp.delete_cookie("token")
            return resp
        case "GET":
            return wrappers.render_template("auth/change_password.html", username=session[USERNAME_TITLE])
        case _:
            return ""


@db.no_perm
def no_perm_redirect(*args, **kwargs):
    return flask.abort(403)

@app.route("/auth/no_permissions")
def no_permissions() -> flask.Response | str:
    return wrappers.render_template("auth/no_perms.html")

@app.route("/repositories")
@db.require_perm(REPOSITORIES_PERMID)
def repositories():
    print("Try render")
    return wrappers.render_template("repositories/index.html")

@app.route("/admin")
@db.require_perm(OPERATOR_PERMID)
def admin_panel():
    return wrappers.render_template("admin/index.html")

@app.route("/admin/permissions")
@db.require_perm(OPERATOR_PERMID)
def admin_permission_list():
    # print(auth.check_permission(auth.get_user_id(), OPERATOR_PERMID) if auth.get_user_id() is not None else "No userid")
    query_result: dict = auth.query_db(
        """SELECT
            id,
            permname,
            parentpermid
        FROM
            Permissions;""")
    responses = query_result["response"]
    perms: list[dict[str, str]] = []
    for response in responses:
        perm = {
            "id": response["id"],
            "permname": response["permname"],
            "parentpermid": response["parentpermid"],
            "depth": auth.count_permission_depth(response["id"]) - 1
        }
        perms.append(perm)
    print(responses)
    return wrappers.render_template("admin/permission_control.html", permissions=perms)

@app.route("/admin/permissions/<int:permid>/<string:action>", methods=["POST"])
@db.require_perm(OPERATOR_PERMID)
def admin_permissions_control(permid: int, action: str):
    print(permid, action)
    username = request.form["username"]
    query_result: dict = auth.query_db("SELECT id FROM Users WHERE username=?", (username,), True)
    response = query_result["response"]
    if response == None:
        return app.redirect("/admin/permissions", 404)
    userid = response["id"]
    match action:
        case "grant":
            auth.grant_permission(userid, permid)
        case "revoke":
            auth.revoke_permission(userid, permid)
    return app.redirect("/admin/permissions", 302)