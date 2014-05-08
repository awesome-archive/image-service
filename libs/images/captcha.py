# coding: utf-8

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

from mixin import ImageMixin
from base64 import b64encode
from StringIO import StringIO
from os import path


class Captcha(ImageMixin):

    _letter_chars = 'abcdefghjkmnpqrstuvwxy'

    _upper_chars = _letter_chars.upper()

    _numbers = ''.join(map(str, range(2, 10)))

    _CHARS = ''.join([_letter_chars, _upper_chars, _numbers])

    def __init__(self, size=(100, 30), chars=None, image_ext='PNG', mode='RGB',
                bg_color=(255, 255, 255), fg_color=(0, 100, 255),
                font_size=20, font='', length=5, draw_line= True, n_line=5,
                draw_point=True, point_chance=20):

        self.level = 5

        self.size = size
        self.mode = mode
        self.width, self.height = size
        self.length = length
        self.chars = self._makechars(chars)
        self.image_ext = image_ext if image_ext else 'PNG'
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font_size = font_size
        self.font = font if font else path.join(path.dirname(__file__), 'fonts/TimesNewRomanBold.ttf')
        self.draw_line = draw_line
        self.n_line = n_line
        self.draw_point = draw_point
        self.point_chance = point_chance

        self.image = None

    def _makechars(self, chars):
        if not chars:
            return ''.join(random.sample(self._CHARS, self.length))
        elif len(chars) < self.length:
            return chars + ''.join(random.sample(self._CHARS, self.length - len(chars)))
        else:
            return chars[0:self.length]

    def make(self):
        # 创建画布
        self.image = Image.new(self.mode, self.size, self.bg_color)
        # 创建画笔
        self.draw = ImageDraw.Draw(self.image)

        self._create_lines()
        self._create_point()
        self._create_strs()
        self._create_transform()

        output = StringIO()
        self.image.save(output, self.image_ext)
        contents = output.getvalue()
        output.close()

        return contents

    def _create_lines(self):
        if not self.draw_line:
            return

        for i in range(self.n_line):
            begin = (random.randint(0, self.width), random.randint(0, self.height))
            end = (random.randint(0, self.width), random.randint(0, self.height))
            self.draw.line([begin, end], fill=self.rand_rgb())

    def _create_point(self):
        if not self.draw_point:
            return

        chance = min(100, max(0, int(self.point_chance)))

        for w in xrange(self.width):
            for h in xrange(self.height):
                _ = random.randint(0, 100)
                if _ > 100 - chance:
                    self.draw.point((w, h), fill=self.rand_rgb())

    def _create_strs(self):
        chars = ' %s ' % ' '.join(list(self.chars))
        font = ImageFont.truetype(self.font, self.font_size)
        font_width, font_height = font.getsize(chars)

        self.draw.text(
            ((self.width - font_width) / 3, (self.height - font_height) / 3),
            chars, font=font, fill=self.fg_color
        )


    def _create_transform(self):
        params = [1 - float(random.randint(1, 2)) / 100,
            0,
            0,
            0,
            1 - float(random.randint(1, 10)) / 100,
            float(random.randint(1, 2)) / 500,
            0.001,
            float(random.randint(1, 2)) / 500
        ]

        self.image = self.image.transform(self.size, Image.PERSPECTIVE, params)
        self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)


if __name__ == '__main__':
    captcha = Captcha(chars='', length=4, fg_color='#ff0000')
    print b64encode(captcha.make())