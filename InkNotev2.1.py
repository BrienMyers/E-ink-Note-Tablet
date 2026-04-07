from multiprocessing.pool import INIT
import numpy
import threading
import board
import time
from PIL import Image,ImageDraw,ImageFont
from pisugar import PiSugarServer

#Digitizer Code
# Use for I2C
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

irq_dio = None  # don't use an irq pin by default
# uncomment for optional irq input pin so we don't continuously poll the I2C for touches
# irq_dio = digitalio.DigitalInOut(board.A0)
tsc = adafruit_tsc2007.TSC2007(i2c, irq=irq_dio)
#Setting for old digitizer
#Old digitizer needed minus 100 to yPos to work new doesn't
#tsc.swap_xy = True
#tsc.invert_y = True

#E-ink Code
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2
import adafruit_tsc2007

pisugar = PiSugarServer()
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

imgUI = Image.open(os.path.join(picdir, 'InkNoteUI.bmp'))
imgUIRed = Image.open(os.path.join(picdir, 'InkNoteUIRed.bmp'))
imgMenu = Image.open(os.path.join(picdir, 'MenuUI.bmp'))
imgMenuBack = Image.new('RGB', (widthPx, heightPx), 'white')
imgMenuBackRed = Image.new('RGB', (widthPx, heightPx), 'white')

imgDraw = Image.new('RGB', (drawWidth, drawHeight), 'white') #Creates a new image 
imgDrawRed = Image.new('RGB', (drawWidth, drawHeight), 'white')
drawImg = ImageDraw.Draw(imgDraw)
drawImgRed = ImageDraw.Draw(imgDrawRed)
aryDraw = numpy.array(imgDraw)

imgSaveOptions = Image.open('SaveOptions.bmp') 
imgLoadOptions = Image.open('LoadOptions.bmp')

#imgDraw.putpixel((position),(color))
#img.save('drawTemp.bmp', 'BMP')

colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0,)
colorRed = (255, 0, 0)
#drawColor = colorBlack
#thickness = 2

imgFull = Image.new('1', (widthPx, heightPx), 255)
imgFullRed = Image.new('1', (widthPx, heightPx), 255)

#Merge the two images before performing partial update or display to screen
UIBox = (0, 0)
drawBox = (0, 100)

#imgFull.paste(imgUI, UIBox)
#imgFull.paste(imgDraw, drawBox)

#imgFullRed.paste(imgUIRed, UIBox)
#imgFullRed.paste(imgDrawRed, drawBox)

#epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFullRed))

#epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFull))

#Update Drawing area when drawing
#epd.display_Partial(epd.getbuffer(imgFull),imgDraw, 100, 0, 800, 480)


#epd.display_Partial(epd.getbuffer(imgFull), imgMenu, 120, 200, 360, 600)

def checkBattery():
    #poll the raspberry pi for battery percentage
    imgFull.draw.line([(300,34.8),(375, 34.8)], fill=colorBlack, width=2.784, joint=None)
    battery_level = pisugar.get_battery_level()
    if 0 <= battery_level <= 25:
        imgFull.draw.rounded_rectangle([303, 6, 319, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([321, 6, 337, 32], 2, colorWhite, outline=None, width=1)
        imgFull.draw.rounded_rectangle([339, 6, 355, 32], 2, colorWhite, outline=None, width=1)
        imgFull.draw.rounded_rectangle([357, 6, 373, 32], 2, colorWhite, outline=None, width=1)
    if 25 < battery_level <= 50:  
        imgFull.draw.rounded_rectangle([303, 6, 319, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([321, 6, 337, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([339, 6, 355, 32], 2, colorWhite, outline=None, width=1)
        imgFull.draw.rounded_rectangle([357, 6, 373, 32], 2, colorWhite, outline=None, width=1)

    if 50 < battery_level <= 75:
        imgFull.draw.rounded_rectangle([303, 6, 319, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([321, 6, 337, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([339, 6, 355, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([357, 6, 373, 32], 2, colorWhite, outline=None, width=1)
    if 75 < battery_level <= 100:
        imgFull.draw.rounded_rectangle([303, 6, 319, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([321, 6, 337, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([339, 6, 355, 32], 2, colorBlack, outline=None, width=1)
        imgFull.draw.rounded_rectangle([357, 6, 373, 32], 2, colorBlack, outline=None, width=1)

def initialize_InkNote():
    checkBattery()
    imgFull.paste(imgUI, UIBox)
    imgFull.paste(imgDraw, drawBox)

    imgFullRed.paste(imgUIRed, UIBox)
    imgFullRed.paste(imgDrawRed, drawBox)

    epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFullRed))


def update_Screen():
    checkBattery()
    imgFull.paste(imgUI, UIBox)
    imgFull.paste(imgDraw, drawBox)
    imgFullRed.paste(imgUIRed, UIBox)
    imgFullRed.paste(imgDrawRed, drawBox)
    epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFullRed))
    return

def save():
    #Paste saveui to full image
    #display full image
    #while loop for selection options
        #Option for save as BMP
        #Option for Exporting
            #Option for save as PNG
            #Option for save as JPG
                #Option for image upscaling
    placeholder1 = 1

def load():
    #Paste Load UI to full image
    #Paste all saved bmp to full image as thumbnails/preview images
    #while loop for selecting which image to load
        #paste saved image to draw area
        #display full image
        #return to menu then main
    placeholder2 = 2

def menu():
    imgMenuBack.paste(imgMenu, (120, 200))
    #epd.display_Partial(epd.getbuffer(imgMenuBack), 120, 200, 360, 600)
    epd.display(epd.getbuffer(imgMenuBack), epd.getbuffer(imgMenuBackRed))
    navMenu = True
    keepDrawing = True

    while navMenu == True:
        point = tsc.touch
        if point["pressure"] < 20: # ignore touches with no 'pressure' as false
            continue
        yPos = int(point["y"]*yscale)
        xPos = int(point["x"]*xscale)
        if 120 <= xPos <= 360:
            if 200 >= yPos <= 300:  #Return to main function
                navMenu = False
                update_Screen()
                break
            if 300 > yPos <= 400:   #Save/Export File
                #Display ui for saving as bmp or png/jpg
                #save drawing area as image into saved folder in the file format chosen
                update_Screen()
                continue
            if 400 > yPos <= 500:   #Load saved file
                #Display ui for all the saved bmp files
                #Load chosen saved image into drawing area
                update_Screen()
                continue
            if 500 > yPos <= 600:   #Quit app
                keepDrawing = False
                return keepDrawing
                
            #epd.display_Partial(epd.getbuffer(imFull), 120, 200, 360, 600)
        return keepDrawing

def draw_Pixels(radius, color):
    circleColor = color
    noting = True
    while noting == True:
        while tsc.touched:
            point = tsc.touch
            if point["pressure"] < 20: # ignore touches with no 'pressure' as false
                continue
            #yPos = int(point["y"]*yscale)
            #xPos = int(point["x"]*xscale)
            yPos = int((point["y"]*yscale))
            xPos = int(point["x"]*xscale)
            if circleColor == colorBlack:
                drawImg.circle((xPos,yPos), radius, circleColor, circleColor, 1)
                #drawImg.putpixel((yPos,xPos),drawColor) # Edit image based on coordinates of points touched
            if circleColor == colorRed:
                drawImgRed.circle((xPos,yPos), radius, colorBlack, colorBlack, 1)
                #drawImgRed.putpixel((yPos,xPos),colorBlack) # Edit image based on coordinates of points touched
            if circleColor == colorWhite:
                drawImg.circle((xPos,yPos), radius, circleColor, circleColor, 1)
                drawImgRed.circle((yPos,xPos), radius, circleColor, circleColor, 1)
                #drawImg.putpixel((yPos,xPos),drawColor) # Edit image based on coordinates of points touched
                #drawImgRed.putpixel((yPos,xPos),colorBlack) # Edit image based on coordinates of points touched
        time.sleep(1)
        noting = False
    update_Screen()
    return


def main():
    initialize_InkNote()
    drawing = True
    drawColor = colorBlack
    thickness = 2

    while drawing == True:
        if tsc.touched:
            while tsc.touched:
                point = tsc.touch
                if point["pressure"] < 20:  # ignore touches with no 'pressure' as false
                    continue
                # Scale coordinates from touch screen to resolution of drawing area
                yPos = int(point["y"]*yscale)
                xPos = int(point["x"]*xscale)
                if yPos <= 100:
                    #Quit from program
                    if xPos <=100:
                        drawing = menu()
                        if drawing == False:
                                epd.Clear()
                                epd.sleep()
                                quit()
                        break
                    #Change color of pen
                    if  420 >= xPos <= 480: #old x-min = 433
                        if  0 <= yPos <= 37:
                            drawColor = colorWhite
                        if 38 <= yPos <= 62:
                            drawColor = colorBlack
                        if  63 <= yPos <= 100:
                            drawColor = colorRed
                            break
                    #Change thickness of pen
                    if yPos <= 50:
                        if 167 >= xPos <= 200:
                            thickness = 2
                        if 200 > xPos <= 235:
                            thickness = 3
                        if 235 > xPos <= 267:
                            thickness = 5
                        if 267 > xPos <= 300:
                            thickness = 7
                            break
                if yPos > 100:
                    draw_Pixels(thickness, drawColor)
                
    epd.Clear()
    epd.sleep()

main()
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

