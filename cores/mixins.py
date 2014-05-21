# coding: utf-8

from pymongo import MongoClient
from bottle import cached_property
from functools import wraps
import time

from cores.constants import Constants


class MongoMixin(object):
    @cached_property
    def db(self):
        connection = MongoClient()

        db = None
        if connection:
            db = connection[Constants.MONGO_DATABASE]

        return db

    @cached_property
    def captcha_coll(self):
        coll = None
        if self.db is not None:
            coll = self.db[Constants.MONGO_CAPTCHA_COLL]
        if coll is not None:
            def wraps_find_one(func):
                """ 重新封装fine_one, 查找captcha时,
                始终将 used 置为 True"""

                @wraps(func)
                def _(*args, **kwargs):
                    update_used = kwargs.pop('update_used') if 'update_used' in kwargs else True
                    expires = kwargs.pop('expires') if 'expires' in kwargs \
                                                           and kwargs['expires'] is not None \
                        and str(kwargs['expires']).isdigit else 3600
                    expires = time.time() + float(expires)

                    result = func(*args, **kwargs)
                    if result is not None and update_used:
                        coll.update({'_id': result['_id']}, {'$set': {'used': True, 'expires': expires}})

                    return result

                return _

            coll.find_one = wraps_find_one(coll.find_one)

        return coll

    def captcha_coll_available_count(self):
        if self.db is not None:
            return self.captcha_coll.find({'used': False}).count()
