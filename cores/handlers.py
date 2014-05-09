# coding: utf-8

from .app import app

@app.get(r'/captcha/token')
def token():
    return
