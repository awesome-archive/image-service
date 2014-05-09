# coding: utf-8

from StringIO import StringIO
from base64 import b64encode


class Base(object):
    def __init__(self):
        self.image = None
        self.image_ext = 'PNG'

    def bytes(self):
        self.make()
        return self.image.tostring()

    def stream(self):
        self.make()
        content = None
        if self.image is not None:
            output = StringIO()
            self.image.save(output, self.image_ext)
            content = output.getvalue()
            output.close()

        return content

    def base64(self):
        output = self.stream()
        if output is not None:
            return b64encode(output)

    def save(self, filename):
        self.make()
        if self.image is not None:
            self.image.save(filename, self.image_ext)

