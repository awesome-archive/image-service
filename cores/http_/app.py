# coding: utf-8

from bottle import Bottle, run as _run, cached_property, JSONPlugin, HTTPResponse
from bottle import LocalResponse as _LocalResponse, GunicornServer
from bottle import LocalRequest as _LocalRequest
from json import dumps
from functools import wraps

from ..constants import Constants
from cores.mixins import MongoMixin
from bson import json_util


class App(Bottle, MongoMixin):
    pass


class LocalRequest(_LocalRequest):
    pass


class LocalResponse(_LocalResponse):
    pass


def strip_path_middleware(wsgi):
    @wraps(wsgi)
    def _(environ, start_response):
        environ['PATH_INFO'] = environ['PATH_INFO'].rstrip('/')
        return wsgi(environ, start_response)

    return _


app = App()
app.wsgi = strip_path_middleware(app.wsgi)
response = LocalResponse()
request = LocalRequest()

app.autojson = False
app.install(JSONPlugin(json_dumps=lambda s: dumps(s, default=json_util.default)))


@app.hook('after_request')
def update_image_status():
    pass


def run(host='127.0.0.1', port='5002', debug=False):
    _run(app, host=host, port=port, debug=debug, server=GunicornServer,
         worker_class='gevent',
         proc_name=Constants.PROC_NAME,
         workers=4, timeout=20)


