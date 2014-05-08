# coding: utf-8

import Image
import ImageFont
import ImageDraw

text = "EwWIieAT"
im = Image.new("RGB",(130,35), (255, 255, 255))
dr = ImageDraw.Draw(im)
font = ImageFont.truetype("TimesNewRomanBold.ttf", 24)
#simsunb.ttf 这个从windows fonts copy一个过来
dr.text((10, 5), text, font=font, fill="#000000")
im.show()
im.save("t.png")
