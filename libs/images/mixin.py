# coding: utf-8

from random import randint


_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}
_HEX_CHAR_ARR = map(lambda _str: str(_str)[-1].upper(), [hex(i) for i in xrange(16)])
_HEXDEC.update({v: int(v, 16) for v in '0123456789abcdefABCDEF'})

LOWERCASE, UPPERCASE = 'x', 'X'


class ImageMixin(object):

    _level = 8

    def rand_hex(self):
        char = '#'
        _HEX_CHAR_ARR = map(lambda _str: str(_str)[-1].upper(), [hex(i) for i in xrange(16)])

        for position in xrange(6):
            char += _HEX_CHAR_ARR[randint(self.level, 15)]

        return char

    def rand_rgb(self):
        return self.hex_to_rgb(self.rand_hex())

    @staticmethod
    def hex_to_rgb(hex_str):
        hex_str = str(hex_str).strip('#')
        if len(hex_str) == 3:
            return _HEXDEC[hex_str[0]], _HEXDEC[hex_str[1]], _HEXDEC[hex_str[2]]
        elif len(hex_str) in (5, 6):
            return _HEXDEC[hex_str[0:2]], _HEXDEC[hex_str[2:4]], _HEXDEC[hex_str[4]]
        else:
            raise ArgumentError(hex_str)

    @staticmethod
    def rgb_to_hex(rgb, lettercase=LOWERCASE):
        return format(rgb[0]<<16 | rgb[1]<<8 | rgb[2], '06'+lettercase)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if value > 15 or value < 0:
            raise ValueError('color level in [0, 15]')

        self._level = value

class ArgumentError(Exception):
    pass

if __name__ == '__main__':
    mixin = ImageMixin()
    print mixin.rand_rgb()
    print mixin.rand_hex()
    print mixin.hex_to_rgb('#1e14cd')
    print mixin.rgb_to_hex((239, 171, 223))
