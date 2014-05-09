# coding: utf-8

from .app import app
from .constants import Constants

@app.get(r'/captcha/token')
def token():
    app.db[Constants.MONGO_DATABASE].insert({'nihao': 'nihao'})
    count = app.db[Constants.MONGO_DATABASE].count()
    return str(count)
