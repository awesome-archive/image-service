# -*- coding: utf-8 -*-
  #AUTHOR: yeshengzou # # gmail.com
  #DATE: 2012.4.23
#LICENCE: GPLv3

import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from random import randint
from cStringIO import StringIO

CHAR = 'acdefghijkmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY345789'
LEN = len(CHAR) - 1
PADDING = 30
X_SPACE = 10#两个字符之间最少相隔多少个像素
TRY_COUNT = 30 #随机字符的位置尝试最多多少次,避免死循环
WIDTH = 70
HEIGHT = 40
FONT = ImageFont.truetype('./libs/images/fonts/Didot.ttf', 20)

def gen():
    im = Image.new('1', (WIDTH, HEIGHT), 'white')
    draw = ImageDraw.Draw(im)
    w, h = im.size

    #S = [(x, y, 'c')]
    S = []
    x_list = []
    y_list = []
    n = 0
    while True:
        n += 1
        if n > TRY_COUNT:
            break
        x = randint(0, w - PADDING)
        flag = True
        for i in x_list:
            if abs(x - i) < X_SPACE:
                flag = False
                continue
            if not flag:
                break
        if not flag:
            continue

        y = randint(0, h - PADDING)
        x_list.append(x)
        y_list.append(y)
        S.append((x, y, CHAR[randint(0, LEN)]))
        if len(S) == 4:
            break

    for x, y, c in S:
        draw.text((x, y), c, font=FONT)

    #加3根干扰线
    for i in range(3):
        x1 = randint(0, (w - PADDING) / 2)
        y1 = randint(0, (h- PADDING / 2))
        x2 = randint(0, w)
        y2 = randint((h - PADDING / 2), h)
        draw.line(((x1, y1), (x2, y2)), fill=0, width=1)

    S.sort(lambda x, y: 1 if x[0] > y[0] else -1)
    char = [x[2] for x in S]
    fileio = StringIO()
    im.save(fileio, 'gif')
    im.show()
    return ''.join(char), fileio

if __name__ == '__main__':
    print gen() 
