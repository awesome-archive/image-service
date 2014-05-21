# coding: utf-8

from json import dumps


class Constants(object):
    MONGO_DATABASE = 'image-service'
    MONGO_CAPTCHA_COLL = 'captcha'
    PROC_NAME = 'ImageService'

    OBJECTS = {}


class _Meta(type):
    def __new__(klass, name, bases, attrs):
        super_new = super(_Meta, klass).__new__
        parents = [b for b in bases if isinstance(b, _Meta)]

        if not parents:
            return super_new(klass, name, bases, attrs)

        new_cls = super_new(klass, name, bases, attrs)
        Constants.OBJECTS[name] = new_cls

        return new_cls


class _object(object):
    def __init__(self, *ignore_args, **kwargs):
        del ignore_args

        for val in dir(self):
            if val.startswith('_'):
                continue

            attr = getattr(self, val)

            if not callable(attr):
                self.__dict__[val] = kwargs.get(val, attr)

    def jsonencode(self):
        _dict = self.to_dict()
        return dumps(_dict)

    def to_dict(self):
        _dict = {}
        for key, item in self.__dict__.iteritems():
            if key.startswith('_'):
                continue
            if isinstance(item, self.__class__):
                _dict[key] = item.to_dict()
            _dict[key] = item

        return _dict


_object = _Meta('_object', (_object,), {})


class CaptchaObject(_object):
    text = ''
    uuid = ''
    stream = ''
    create_time = 0
    used = False
    random = None
    extension = 'png'
