# coding: utf-8

from .app import app
from .constants import Constants

@app.get(r'/captcha/token')
def token():
    app.captcha_coll.insert({'nihao': 'buhao'})
    count = app.captcha_coll.count()
    return str(count)
