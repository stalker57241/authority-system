from flask import request # type: ignore
import flask
import app.auth as auth
import hashlib
from app.config import *
from app.db import init_db
import time

init_db()

@app.route("/")
def index():
    return flask.render_template("index.html")

# @app.route("/static/<filename>.<fmt>")
# def static(filename: str, fmt: str):
#     match fmt:
#         case "css":
#             with open(f"web/static/{filename}.css", "r") as file:
#                 return "\n".join(file.readlines())
#         case _:
#             return ""

@app.route("/users/<username>")
def userpage(username: str):
    email: str = auth.query_db("SELECT email FROM Users WHERE username=?", (username,), True)["response"]["email"]
    return flask.render_template("users/user.html", username=username, email=email)

@app.route("/auth/login")
def login():
    return flask.render_template("auth/login.html")

@app.route("/auth/register", methods=['POST', 'GET'])
def register():
    match request.method:
        case 'POST':
            password = hashlib.sha256(request.form['password'].encode()).hexdigest()
            confirm_password = hashlib.sha256(request.form['confirm_password'].encode()).hexdigest()
            if not auth.Validator.passwords(password, confirm_password): return flask.redirect('/', 422)
            if not auth.Validator.username(request.form['username']):    return flask.redirect('/', 422)
            if not auth.Validator.email(request.form['email']):          return flask.redirect('/', 422)
            email = request.form['email']
            print('POST', request.form)
            idx = register_user(request.form['username'], email, password)

            expire_secs = time.time() + 60 * 60 * 24 # Secs -> minutes -> hours -> day
            token = hashlib.sha256()
            token.update(request.form["username"].encode())
            token.update(f"{expire_secs}".encode())
            
            register_token(idx, token.hexdigest(), expire_secs)

            resp = flask.make_response(
                flask.render_template("auth/registration_successful.html", username=request.form["username"])
            )

            resp.set_cookie("username", request.form["username"])
            resp.set_cookie("token", token.hexdigest())

            return resp
        case 'GET':
            return flask.render_template("auth/register.html")
        case _:
            return "Invalid method"


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
                request.cookies.get(USERNAME_COOKIE_TITLE), old_password
            ), True)["response"]) == 0: return flask.redirect("/", 403)
            if not auth.Validator.passwords(new_password, confirm_password): flask.redirect("/", 422)
            resp = auth.query_db("SELECT id, expired FROM UserTokens WHERE token=?", (request.cookies.get(TOKEN_COOKIE_TITLE),), True)["response"]
            if int(resp["expired"]) < time.time():
                auth.query_db("DELETE FROM UserTokens WHERE token=?", (request.cookies.get(TOKEN_COOKIE_TITLE),))
                return flask.redirect("/", 403)
            idx = resp["idx"]
            auth.query_db("UPDATE Users SET password=? WHERE id=?", (new_password, idx))
            resp = flask.make_response(flask.render_template("auth/password_changed.html"))
            resp.delete_cookie("username")
            resp.delete_cookie("token")
            return resp
        case "GET":
            return flask.render_template("auth/change_password.html", username=request.cookies.get(USERNAME_COOKIE_TITLE))
        case _:
            return ""