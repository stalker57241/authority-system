import flask
from flask import session
from jinja2.environment import Template
from app.config import *


def render_template(
        template_name_or_list: str | Template | list[str | Template],
        *args, **kwargs
):
    try:
        username = session[USERNAME_TITLE]
        if username == None: raise KeyError("None")
        return flask.render_template(template_name_or_list, username=username, *args, **kwargs)
    except BaseException:
        return flask.render_template(template_name_or_list, *args, **kwargs)
