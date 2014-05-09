# coding: utf-8

from bottle import Bottle, run as _run, cached_property, JSONPlugin, HTTPResponse
from bottle import LocalResponse as _LocalResponse
from bottle import LocalRequest as _LocalRequest
from json import dumps, JSONEncoder
import pymongo
import bson


from .constants import Constants
from utils.mixins import MongoMixin

class App(Bottle, MongoMixin):
    pass

class LocalRequest(_LocalRequest):
    pass


class LocalResponse(_LocalResponse):
    pass


def mongo_dumps(obj):
    # convert all iterables to lists
    if hasattr(obj, '__iter__'):
        return list(obj)
    # convert cursors to lists
    elif isinstance(obj, pymongo.cursor.Cursor):
        return list(obj)
    # convert ObjectId to string
    elif isinstance(obj, bson.objectid.ObjectId):
        return unicode(obj)
    # dereference DBRef
    elif isinstance(obj, bson.dbref.DBRef):
        return db.dereference(obj) # db is the incetance database
    # convert dates to strings
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
        return unicode(obj)
    return json.JSONEncoder.default(self, obj)


app = App()
response = LocalResponse()
request = LocalRequest()

app.autojson = False
app.install(JSONPlugin(json_dumps=lambda s: dumps(s, default=mongo_dumps)))


def run(host='127.0.0.1', port='5002', debug=False):
    _run(app, host=host, port=port, debug=debug)


