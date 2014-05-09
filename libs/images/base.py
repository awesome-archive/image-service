# coding: utf-8

from StringIO import StringIO
from base64 import b64_encode


class Base(object):
    def __init__(self):
        self.image = None
        self.image_ext = 'PNG'

    def show(self):
        output = None
        if self.image is not None:
            output = StringIO()
            self.image.save(output, self.image_ext)
            content = output.getvalue()
            output.close()

        return output

    def show_base64(self):
        output = self.show()
        if output is not None:
            return b64_encode(output)

    def save(self, filename):
        if self.image is not None:
            self.image.save(filename, self.image_ext)

