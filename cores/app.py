# coding: utf-8

from bottle import Bottle, run as _run
from bottle import LocalResponse as _LocalResponse
from bottle import LocalRequest as _LocalRequest


class App(Bottle):
    pass


class LocalRequest(_LocalRequest):
    pass


class LocalResponse(_LocalResponse):
    pass


app = App()
response = LocalResponse()
request = LocalRequest()


def run(host='127.0.0.1', port='5002', debug=False):
    _run(app, host=host, port=port, debug=debug)


