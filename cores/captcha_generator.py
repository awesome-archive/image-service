# coding: utf-8

from libs.images import Captcha
from utils.mixins import MongoMixin
from cores.constants import CaptchaObject

from threading import Thread, Condition
import uuid
import time


class CaptchaGenerator(MongoMixin):
    def __init__(self, min_count=10, check_interval=10):
        self.condition = Condition()
        self.min_count = min_count

        self.check_captcha_thread = CheckCaptchaCountThread(
            self.condition, self.captcha_coll, self.min_count,
            check_interval
        )
        self.check_captcha_thread.setDaemon(True)

    def workloop(self):
        self.condition.acquire()  # 获得锁
        self.check_captcha_thread.start()  # 启动查询数量线程

        while 1:
            self.condition.wait()  # 开始等待查询线程通知
            curr_count = self.captcha_coll.count()
            new_captcha_count = self.min_count - curr_count
            for _ in xrange(new_captcha_count):  # 开始循环创建验证码
                text, captcha_str = self.generat_captcha()
                self.save(text, captcha_str)
                time.sleep(0.5)

            # 验证码创建完毕之后通知查询线程继续查询
            self.condition.notify()

    def generat_captcha(self, char_lenght=4):
        captcha = Captcha(length=char_lenght)
        text = captcha.chars
        content = captcha.show_base64()

        return text, content

    def save(self, text, captcha_str):
        _object = CaptchaObject(
            text=text,
            stream=captcha_str,
            create_time=time.time(),
            uuid=uuid.uuid1().__str__()
        )

        # print _object.to_dict()

        self.captcha_coll.insert(_object.to_dict())


class CheckCaptchaCountThread(Thread):
    def __init__(self, condition, coll, min_count=100, check_interval=10):
        Thread.__init__(self)
        self.coll = coll
        self.condition = condition
        self.min_count = min_count
        self.check_interval = check_interval

    def run(self):
        self.condition.acquire()  # 取得锁

        while 1:
            curr_count = self.coll.count()
            if curr_count < self.min_count:
                self.condition.notify()

                self.condition.wait()  # 线程挂起等闲创建验证码主线程通知

            time.sleep(self.check_interval)
