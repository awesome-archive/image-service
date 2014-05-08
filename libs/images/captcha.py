# coding: utf-8

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random


class Captcha(object):

    _letter_chars = 'abcdefghjkmnpqrstuvwxy'

    _upper_chars = _letter_chars.upper()

    _numbers = ''.join(map(str, range(2, 10)))

    _CHARS = ''.join([_letter_chars, _upper_chars, _numbers])

    def __init__(self, size=(120, 30), chars=None, image_ext='png', mode='RGB',
                bg_color=(255, 255, 255), fg_color=(0, 0, 255),
                font_size=16, font='', length=5, draw_line= True, n_line=5,
                draw_point=True, point_chance=20):
        self.size = size
        self.width, self.height = size
        self.length = length
        self.chars = self._makechars(chars)
        self.image_ext = image_ext
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font_size = font_size
        self.font = font
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

    def _create_lines(self):
        if not self.draw_line:
            return

        for i in range(self.n_line):
            begin = (random.randint(0, self.width), random.randint(0, self.height))
            end = (random.randint(0, self.width), random.randint(0, self.height))
            self.draw.line([begin, end], fill=(0, 0, 0))

    def _create_point(self):
        if not self.draw_point:
            return

        chance = min(100, max(0, int(self.point_chance)))

        for w in xrange(self.width):
            for h in xrange(self.height):
                _ = random.randint(0, 100)
                if _ > 100 - chance:
                    self.draw.point((w, h), fill=(0, 0, 0))

    def _create_strs(self):
        chars = self.chars
        font = ImageFont.truetype(self.font_type, self.font_size)
        font_width, font_height = font.getsize(chars)
        self.draw.text(
            ((self.width - font_width) / 3, (self.height - font_height) / 3),
            chars, font=font, fill=self.fg_color
        )


if __name__ == '__main__':
    captcha = Captcha(chars='', length=4)