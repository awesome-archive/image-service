# coding: utf-8

from pymongo import MongoClient
from bottle import cached_property
from functools import wraps

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
            def warps_find_one(func):
                @wraps(func)
                def _(*args, **kwargs):
                    result = func(*args, **kwargs)
                    if result is not None:
                        coll.update({'used': True}, result)

                    return result
            coll.find_one = wraps_find_one(coll.find_one)

        return coll

    def captcha_coll_available_count(self):
        if self.db is not None:
            return self.captcha_coll.find({'used': False}).count()
