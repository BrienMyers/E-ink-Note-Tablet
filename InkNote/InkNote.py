import numpy

# Digitizer Code
import board

import adafruit_tsc2007

# Use for I2C
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

irq_dio = None  # don't use an irq pin by default
# uncomment for optional irq input pin so we don't continuously poll the I2C for touches
# irq_dio = digitalio.DigitalInOut(board.A0)
tsc = adafruit_tsc2007.TSC2007(i2c, irq=irq_dio)
tsc.swap_xy = True
tsc.invert_y = True

#E-ink Code
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2
import time
from PIL import Image,ImageDraw,ImageFont

epd = epd7in5b_V2.EPD()
epd.init_Fast()
epd.Clear()

#font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
#font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

#InkNote Code
widthPx = 480
heightPx = 800
xscale = widthPx/4095
yscale = heightPx/4095
drawWidth = 480
drawHeight = 700
drawX = drawWidth/4095
drawY = drawHeight/4095

drawing = True

imgUI = Image.open('InkNoteUI.bmp')
imgUIRed = Image.open('InkNoteUIRed.bmp')
imgMenu = Image.open('MenuUI.bmp')

imgDraw = Image.new('RGB', (drawWidth, drawHeight), 'white') #Creates a new image 
imgDrawRed = Image.new('RGB', (drawWidth, drawHeight), 'white')
drawImg = ImageDraw.Draw(imgDraw)
drawImgRed = ImageDraw.Draw(imgDrawRed)
aryDraw = numpy.array(imgDraw)

#imgDraw.putpixel((position),(color))
#img.save('drawTemp.bmp', 'BMP')

colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0,)
colorRed = (255, 0, 0)
drawColor = colorBlack

thickness = 2

imgFull = Image.new('1', (widthPx, heightPx), 255)
imgFullRed = Image.new('1', (widthPx, heightPx), 255)

#Merge the two images before performing partial update or display to screen
UIBox = (0, 0)
drawBox = (0, 100)

imgFull.paste(imgUI, UIBox)
imgFull.paste(imgDraw, drawBox)

imgFullRed.paste(imgUIRed, UIBox)
imgFullRed.paste(imgDrawRed, drawBox)

epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFullRed))

#epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFull))

#Update Drawing area when drawing
#epd.display_Partial(epd.getbuffer(imgFull),imgDraw, 100, 0, 800, 480)


#epd.display_Partial(epd.getbuffer(imgFull), imgMenu, 120, 200, 360, 600)

def update_Screen():
    imgFull.paste(imgUI, UIBox)
    imgFull.paste(imgDraw, drawBox)
    imgFullRed.paste(imgUIRed, UIBox)
    imgFullRed.paste(imgDrawRed, drawBox)
    epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFullRed))
    return

def draw_Pixels():
    while tsc.touched:
        point = tsc.touch
        if point["pressure"] < 50: # ignore touches with no 'pressure' as false
            continue
        yPos = int(point["x"]*drawY)
        xPos = int(point["y"]*drawX)
        if drawColor == colorBlack:
            drawImg.circle((yPos,xPos), thickness, drawColor, drawColor, 1)
            #drawImg.putpixel((yPos,xPos),drawColor) # Edit image based on coordinates of points touched
        if drawColor == colorRed:
            drawImgRed.circle((yPos,xPos), thickness, colorBlack, drawColor, 1)
            #drawImgRed.putpixel((yPos,xPos),colorBlack) # Edit image based on coordinates of points touched
        if drawColor == colorWhite:
            drawImg.circle((yPos,xPos), thickness, drawColor, drawColor, 1)
            drawImgRed.circle((yPos,xPos), thickness, drawColor, drawColor, 1)
            #drawImg.putpixel((yPos,xPos),drawColor) # Edit image based on coordinates of points touched
            #drawImgRed.putpixel((yPos,xPos),colorBlack) # Edit image based on coordinates of points touched
    update_Screen()
    return

while drawing == True:
    if tsc.touched:
        while tsc.touched:
            point = tsc.touch
            if point["pressure"] < 100:  # ignore touches with no 'pressure' as false
                continue
            # Scale coordinates from touch screen to resolution of drawing area
            yPos = int(point["y"]*yscale)
            xPos = int(point["x"]*xscale)
            if yPos <= 100:
                #Quit from program
                if xPos <=100:
                    drawing = False
                #Change color of pen
                if  433 >= xPos <= 480:
                    if  0 <= yPos <= 37:
                        drawColor = colorWhite
                    if 38 <= yPos <= 62:
                        drawColor = colorBlack
                    if  63 <= yPos <= 100:
                        drawColor = colorRed
                        break
                #Change thickness of pen
                if yPos <= 35:
                    if 167 >= xPos <= 200:
                        thickness = 2
                    if 200 > xPos <= 235:
                        thickness = 3
                    if 235 > xPos <= 267:
                        thickness = 5
                    if 267 > xPos <= 300:
                        thickness = 7
            if yPos > 100:
                draw_Pixels()

"""
while  drawing == True:
    if tsc.touched:
        point = tsc.touch
    if point["pressure"] < 100:  # ignore touches with no 'pressure' as false
        continue
    
    # Scale coordinates from touch screen to resolution of drawing area
    xPos = point["x"]*xscale
    yPos = point["y"]*yscale

    #If touched menu button
    if yPos < 100:
        if 0 > xPos < 60:

        #Print Menu Bitmap
            #Continue
            #Save
            #Export
            #Quit
        #Wait for additional screen touched
        #Perform separate actions based on area touched
        #Ignore other touches

    #If thickness touched

    #If touched color button
        #If white touched
            #drawColor = colorWhite
            #draw square around white circle
        #If black touched
            #drawColor = colorBlack
            #draw square around black circle
        #If red touched
            #drawColor = colorRed
            #draw square around red circle

    #If eraser tool button touched
        #drawColor = colorWhite
        #draw square around erase
    
    #If Increase/Decrease pen thickness
        #Increase area of pixels changed around point of contact
    if yPos > 100:
        imgDraw.putpixel((xPos,yPos),drawColor) # Edit image based on coordinates of points touched
        
        #edp.display_Base_color(self, color)

    time.sleep(1.5)  # Wait 1.5 seconds without being touched
    epd.display_Partial(epd.getbuffer(imgFull), imgDraw, 0, 700, 480, 800) # Print bitmap to screen


    exit()
    """
epd.Clear()
epd.sleep()
