# coding: utf-8

from .app import app
from .constants import Constants

@app.get(r'/captcha/token')
def token():
    coll = app.captcha_coll
    return str(count)
