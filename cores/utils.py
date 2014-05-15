# coding: utf-8

from random import randint, random
import time
import uuid

from libs.images.captcha import Captcha
from cores.constants import CaptchaObject


def generat_random_captcha():
    char_lenght = randint(4, 5)

    captcha = Captcha(length=char_lenght)
    text = captcha.chars
    captcha_str = captcha.base64()
    image_ext = captcha.image_ext

    _object = CaptchaObject(
        text=text,
        stream=captcha_str,
        create_time=time.time(),
        uuid=uuid.uuid1().__str__(),
        random=random(),
        extension=image_ext
    )

    return _object
