# coding: utf-8

from .app import app, response, request, HTTPResponse
from .constants import Constants
from random import random
from base64 import b64decode

@app.get(r'/captcha/token')
def token():
    coll = app.captcha_coll
    return str(count)

@app.get(r'/captcha')
@app.get(r'/captcha/<token>')
def captcha(token=None):
    coll = app.captcha_coll
    if token is None:
        rand = random()
        content = coll.find_one({'random': {"$gte": rand}, 'used': False})
        return content
    else:
        content = coll.find_one({'uuid': token, 'used': False})

        if content is not None:
            response.content_type = 'image/%s' % (content['extension'] if 'extension' in content else 'png')
            return b64decode(content['stream'])
        else:
            return HTTPResponse('', status=400)
