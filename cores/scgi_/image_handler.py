# -*- coding: utf-8 -*-

import sys
import time
import cgi
import random
import cStringIO
import ctypes
from os import path

from handler_base import HandlerException, HandlerBase

from wand.image import Image
from wand.color import Color
from wand.api import library

class ImageHandler(HandlerBase):

    fonts_path = None

    def produce(self, env, bodysize, input) :
        """处理 scgi 请求"""
        data = cgi.parse_qs(env['QUERY_STRING'])
        stream = cStringIO.StringIO(input.read(bodysize))

        for i in data:
            data[i] = data[i][0]

        handlers = {
            'captcha': self.captcha,
            'crop':    self.crop,
            'resize':  self.resize,
            'padding': self.padding,
        }

        #self.debug('product %s request.' % env['SCRIPT_NAME'])

        if env['SCRIPT_NAME'] not in handlers:
            raise HandlerException, 'not implement "%s"' % env['SCRIPT_NAME']

        handlers[env['SCRIPT_NAME']](data, stream)

    def captcha(self, data, stream):
        """生成验证码图片"""

        conf = dict(width=150, height=60, fontsize=28, forecolor=None, 
            background=None, imageFormat='PNG')

        conf.update(data)

        width = int(conf['width'])
        height = int(conf['height'])
        fontsize = int(conf['fontsize'])
        fontList = ['AntykwaBold.ttf', 'Didot.ttf', 'TimesNewRomanBold.ttf']
        font = path.join(self.fonts_path, random.choice(fontList))
        sizeY = fontsize + 10
        sizeX = int((width - fontsize * len(conf['width'])) / len(conf['width']))

        forecolor = ('forecolor' in conf) and conf['forecolor'] or 'rgb(000,000,000)'
        background = ('background' in conf) and conf['background'] or 'rgb(255,255,255)'

        wand = library.NewMagickWand()
        drawWand = library.NewDrawingWand()

        library.MagickNewImage(wand, width, height, self.wrapColor(background))
        library.MagickSetFormat(wand, conf['imageFormat'])

        library.DrawSetTextEncoding(drawWand, 'UTF8')
        library.DrawSetFillColor(drawWand, self.wrapColor(forecolor))
        library.DrawSetFont(drawWand, font)
        library.DrawSetFontWeight(drawWand, ctypes.c_size_t(900))
        library.DrawSetTextAntialias(drawWand, True)
        library.DrawAnnotation.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_char_p]

        pos = 0
        for text in conf['text']:
            rorate = random.choice(range(-10, 10))
            library.DrawRotate(drawWand, ctypes.c_double(float(rorate) / 10))
            library.DrawSetFontSize(drawWand, ctypes.c_double(random.choice(range(fontsize - 5, fontsize + 5))))

            library.DrawAnnotation(
                drawWand, 
                int(sizeX + pos * fontsize / (random.choice([10, 11, 12]) / float(10))),
                random.choice(range(sizeY, sizeY + 10)) + rorate, text
            )

            pos = pos + 1

        library.MagickDrawImage(wand, drawWand)
        library.MagickCharcoalImage(wand, ctypes.c_double(1), ctypes.c_double(1))
        library.MagickAddNoiseImage(wand, 4)

        self.respondImg(imgWand = wand, format=conf['imageFormat'])

    def getOptions(self, conf):
        """获得缩略图设置"""
        if ('width' not in conf or 'height' not in conf): 
            raise HandlerException, 'Must provide a width or a height'

        return {
            'width'  : int(conf['width']),
            'height' : int(conf['height']),
            'format' : ('format' in conf) and conf['format'] or 'PNG'
        }

    def crop(self, conf, stream):
        """裁切图片"""

        opt    = self.getOptions(conf)
        img    = Image(file = stream)

        ratio = float(img.width) / float(img.height)

        if ratio > (opt['width'] / opt['height']) :
            h = opt['height']
            w = int(h * ratio)
            x = int((w - opt['width']) / 2)
            y = 0
        else:
            w = opt['width']
            h = int(w / ratio)
            x = 0
            y = int((h - opt['height']) / 2)

        def cropImage(frame):
            library.MagickScaleImage(frame, w, h)
            library.MagickCropImage(frame, opt['width'], opt['height'], x, y)

        img = self.processImg(img, cropImage)

        self.respondImg(img, format = opt['format'])

    def resize(self, conf, stream):
        """按比例缩放"""

        opt    = self.getOptions(conf)
        img    = Image(file = stream)

        ratio = float(img.width) / float(img.height)

        if opt['width'] * opt['height'] == 0:
            if opt['width'] == 0 and opt['height'] == 0:
                size = (800, 600)
            else:
                if opt['width'] == 0:
                    size = (int(opt['height'] * ratio), opt['height'])
                else:
                    size = (opt['width'],  int(opt['width'] / ratio))
        else:
            if ratio > (opt['width'] / opt['height']) :
                size = (opt['width'],  int(opt['width'] / ratio))
            else:
                size = (opt['height'], int(opt['height'] * ratio))

        img = self.processImg(
            img, lambda frame: library.MagickScaleImage(frame, size[0], size[1])
        )

        self.respondImg(img, format = opt['format'])

    def padding(self, conf, stream):
        """补白的形式缩图"""

        opt    = self.getOptions(conf)
        img    = Image(file = stream)

        ratio = float(img.width) / float(img.height)


        if ratio > (opt['width'] / opt['height']) :
            w = opt['width']
            h = int(w / ratio)
            x = 0
            y = int((opt['height'] - h) / 2)
        else:
            h = opt['height']
            w = int(h * ratio)
            x = int((opt['width'] - w) / 2)
            y = 0

        color = self.wrapColor('rgb(255,255,255)')

        wands = []
        def paddingImage(frame):
            thumbWand = library.NewMagickWand()
            library.MagickNewImage(
                thumbWand, opt['width'], opt['height'], color
            )
            library.MagickScaleImage(frame, w , h)
            library.MagickCompositeImage(thumbWand, frame, 40, x, y)
            wands.append(thumbWand)

        img = self.processImg(img, paddingImage)

        imgWand = None

        if len(wands) > 1:
            imgWand = library.NewMagickWand()
            for frame in wands:
                library.MagickAddImage(imgWand, frame)

        else:
            imgWand = wands[0]

        img.wand = imgWand

        self.respondImg(img, format = opt['format'])

    def processImg(self, img, delegate):
        """处理图片"""

        wand = img.wand

        hasMoreImages = library.MagickGetNumberImages(wand) > 1

        if hasMoreImages:
            wand = library.MagickCoalesceImages(wand)
            library.ClearMagickWand(img.wand)
            library.MagickResetIterator(wand)

        while True:

            delegate(wand)

            if not library.MagickNextImage(wand): break

        if hasMoreImages: img.wand = wand

        return img

    def respondImg(self, img = None, imgWand = None, format = 'JPEG', quality = 80):
        """输出图片"""

        blob    = None

        if img is not None and not isinstance(img, Image):
            raise TypeError('image must be a wand.image.Image instance, not ' + repr(img))

        length = ctypes.c_size_t()

        blob_p = library.MagickGetImagesBlob(wand, ctypes.byref(length))

        if blob_p and length.value:
            blob = ctypes.string_at(blob_p, length.value)
            library.MagickRelinquishMemory(blob_p)

        self.respond(blob)

    def wrapColor(self, color):
        """ color to pixelWand """

        pixelWand = library.NewPixelWand()
        library.PixelSetColor(pixelWand, color)
        return pixelWand
