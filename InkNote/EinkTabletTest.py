# *****************************************************************************
# * | File        :	  EinkTabletTest.py
# * | Author      :   Brien Myers
# * | Function    :   Electronic paper tablet program
# * | Info        :
# *----------------
# * | This version:   V0.002
# * | Date        :   2025-12-20
# # | Info        :   python program
# -----------------------------------------------------------------------------

#Needed for E-ink Screen
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from waveshare_epd import epdconfig

#Needed for Touch Screen
"""
import board
import adafruit_tsc2007
i2c = board.I2C()  
irq_dio = None
tsc = adafruit_tsc2007.TSC2007(i2c, irq=irq_dio)
"""

# Display resolution
EPD_WIDTH       = 480
EPD_HEIGHT      = 800

try:
    epd = epd7in5b_V2.EPD()

    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
    fontblox = ImageFont.truetype(os.path.join(picdir, 'Blox2.ttf'), 36)
    fontArcade = ImageFont.truetype(os.path.join(picdir, 'Arcade.ttf'), 36)
    fontPaladin = ImageFont.truetype(os.path.join(picdir, 'PaladinFLF.ttf'), 36)

    Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    Limage_Other = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Limage)
    draw_Himage_Other = ImageDraw.Draw(Limage_Other)
    draw_Himage.text((100, 300), 'Horsecocks are great!', font = fontPaladin, fill = 0)
    epd.display(epd.getbuffer(Limage), epd.getbuffer(Limage_Other))
    time.sleep(5)

    Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    Limage_Other = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Limage)
    draw_other = ImageDraw.Draw(Limage_Other)
    epd.init_Fast()
    Limage = Image.open(os.path.join(picdir, 'testtiger.bmp'))
    Limage_Other = Image.open(os.path.join(picdir, 'testtiger.bmp'))
    epd.display(epd.getbuffer(Limage),epd.getbuffer(Limage_Other))
    draw_Himage.text((200, 200), 'Horsecocks are great!', font = fontPaladin, fill = 0)
    epd.display(epd.getbuffer(Limage),epd.getbuffer(Limage_Other))
    time.sleep(5)

    """
    newX = () * EPD_WIDTH
    newY = () * EPD_HEIGHT

    while True:
        if tsc.touched:
            point = tsc.touch
            if point["pressure"] < 100:  # ignore touches with no 'pressure' as false
                continue
            print("Touchpoint: (%d, %d, %d)" % (point["x"], point["y"], point["pressure"]))
    """

    epd.init()
    epd.Clear()
    epd.sleep()

except KeyboardInterrupt:
    print("Exiting Program...")
    epd.init()
    epd.Clear()
    epd.sleep()
    epd7in5b_V2.epdconfig.module_exit(cleanup=True)
    exit()


