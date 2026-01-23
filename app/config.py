from flask import Flask

app = Flask(__name__)

# Dirs
SCHEMAS_DIR = "schemas"

# Tables
USER_TABLE = "Users"
USER_TOKEN_TABLE = "UserTokens"

# Files
DATABASE = "data.db"
INITIAL_SCHEMA = "initial.sql"

# Titles

USERNAME_COOKIE_TITLE = "username"
TOKEN_COOKIE_TITLE = "token"

