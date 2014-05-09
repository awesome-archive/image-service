# coding: utf-8

from bottle import Bottle, run as _run

class App(Bottle):
    pass

app = App()


def run(host='127.0.0.1', port='5002', debug=False):
    _run(app, host=host, port=port, debug=debug)


