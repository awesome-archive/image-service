# coding: utf-8

from .app import app, response, request, HTTPResponse
from ..constants import Constants
from cores.utils import generat_random_captcha
from random import random
from base64 import b64decode


@app.get(r'/captcha/<token>')
def captcha_token(token=None):
    coll = app.captcha_coll
    content = coll.find_one({'uuid': token, 'used': True}, update_used=False)

    if content is not None:
        response.content_type = 'image/%s' % (content['extension'] if 'extension' in content else 'png')
        return b64decode(content['stream'])
    else:
        return HTTPResponse('', status=400)


@app.get(r'/captcha')
def captcha():
    coll = app.captcha_coll
    rand = random()
    expires = request.params.get('expires')
    content = coll.find_one({'random': {"$gte": rand}, 'used': False}, expires=expires)

    if content:
        return content
    else:
        return generat_random_captcha().to_dict()