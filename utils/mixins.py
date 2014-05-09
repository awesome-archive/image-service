# coding: utf-8

from pymongo import MongoClient
from bottle import cached_property

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
        if self.db is not None:
            return self.db[Constants.MONGO_CAPTCHA_COLL]

    def captcha_coll_available_count(self):
        if self.db is not None:
            return self.captcha_coll.find({'used': False}).count()
