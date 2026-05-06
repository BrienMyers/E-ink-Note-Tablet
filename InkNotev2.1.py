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
exportdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'export')
saveddir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'saved')
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

imgSave = Image.open(os.path.join(picdir, 'SaveOptions.bmp')) 
imgLoad = Image.open(os.path.join(picdir, 'LoadOptions.bmp'))

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
previewBox = (17, 20)

numSaved = 0

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
    #freshBoot = True
    #load(freshBoot)


    imgFull.paste(imgUI, UIBox)
    imgFull.paste(imgDraw, drawBox)

    imgFullRed.paste(imgUIRed, UIBox)
    imgFullRed.paste(imgDrawRed, drawBox)
    checkBattery()

    epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFullRed))

def update_Screen():
    imgFull.paste(imgUI, UIBox)
    imgFull.paste(imgDraw, drawBox)
    imgFullRed.paste(imgUIRed, UIBox)
    imgFullRed.paste(imgDrawRed, drawBox)
    checkBattery()
    epd.display(epd.getbuffer(imgFull), epd.getbuffer(imgFullRed))
    return

def saveconvert(): #Converts and merges the black and red drawing images and returns it
    imgdrawSave = imgDraw.copy()
    imgdrawSaveRed = imgDrawRed.copy()
    imgdrawSave.convert("RGBA")
    imgdrawSaveRed.convert("RGBA")
    drawData = imgdrawSave.getdata()
    redDrawData = imgdrawSave.getdata()

    newDrawData = []

    for item in drawData:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newDrawData.append((255, 255, 255, 0))
        else:
            newDrawData.append(item)

    newRedDrawData = []

    for item in redDrawData:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newRedDrawData.append((255, 255, 255, 0))
        else:
            newRedDrawData.append(item)

    imgdrawSave.putdata(newDrawData)
    imgdrawSaveRed.putdata(newRedDrawData)

    imgdrawSave.paste(imgdrawSaveRed, UIBox)

    finalDrawData = imgdrawSave.getdata()

    finalNewData = []

    for item in redDrawData:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newRedDrawData.append((255, 255, 255, 255))
        else:
            newRedDrawData.append(item)

    imgdrawSave.putdata(finalNewData)

    return imgdrawSave

def saving():
    saving = True
    saveState = ".bmp"
    resolution = (480, 800)

    imgMenuBack.paste(imgSave, UIBox) #Paste to saveui img

    #convert drawImg to Preview
    imgdrawPreview = imgDraw.copy()
    imgdrawPreviewRed = imgDrawRed.copy()
    imgdrawPreview = imgDraw.resize([300, 440])
    imgdrawPreviewRed = imgDrawRed.resize([300, 440])
    
    #Paste saveui to full image
    imgMenuBack.paste(imgdrawPreview, previewBox)
    imgMenuBackRed.paste(imgdrawPreviewRed, previewBox)
    epd.display(epd.getbuffer(imgMenuBack), epd.getbuffer(imgMenuBackRed))  #Diplay saveui

    while saving == True:
        point = tsc.touch
        if point["pressure"] < 20: # ignore touches with no 'pressure' as false
            continue
        yPos = int(point["y"]*yscale)
        xPos = int(point["x"]*xscale)

        #Save
        if (21 <= yPos <= 110 and 325 <= xPos <= 462):
            saveState = ".bmp"
        #Export
        if (138 >= yPos <= 228 and 325 >= xPos <= 462):
            saveState = ".png"
        #PNG
        if (254 >= yPos <= 346 and 325 >= xPos <= 462):
            saveState = ".png"
        #JPEG
        if (373 >= yPos <= 460 and 325 >= xPos <= 462):
            saveState = ".jpg"
        #Resolution
        #480x700
        if (532 >= yPos <= 590 and 23 >= xPos <= 455):
            resolution = (480, 800)
        #960x1400
        if (590 > yPos <= 647 and 23 >= xPos <= 455):
            resolution = (960, 1400)
        #1440x210
        if (647 >= yPos <= 705 and 23 >= xPos <= 455):
            resolution = (1440, 2100)
        #Return
        if (717 >= yPos <= 784 and 39 >= xPos <= 204):
            saving = False
            break
        #confirm
        if (717 >= yPos <= 784 and 282 >= xPos <= 445):
            if saveState == ".bmp":
                imgDraw.save(os.path.join(exportdir, 'NoteBlack' + numSaved + saveState))
                imgDrawRed.save(os.path.join(exportdir, 'NoteRed' + numSaved + saveState))
       
            if (saveState == ".png" or saveState == ".jpg"):
            
                imgExport = saveconvert()
                imgExport.resize(resolution)
                imgExport.save( os.path.join(exportdir, 'Note' + numSaved + saveState))

def quicksave():
    imgDraw.save(os.path.join(exportdir, 'NoteBlack' + numSaved + '.bmp'))
    imgDrawRed.save(os.path.join(exportdir, 'NoteRed' + numSaved + '.bmp'))


def load(firstLoad):
    #Check how many files in saved /2
    #numSaved = 0
    #Paste Load UI to full image
    #Paste all saved bmp to full image as thumbnails/preview images

    loading = True  #while loop for selecting which image to load
    while loading == True:
        point = tsc.touch
        if point["pressure"] < 20: # ignore touches with no 'pressure' as false
            continue
        yPos = int(point["y"]*yscale)
        xPos = int(point["x"]*xscale)
        #if firstLoad == True
            #paste blank space on return
        #if new
            #firstLoad = False
            #check if current img is in saved
            #create new blank img for draw 
        #if load option
            #open draw img and paste to full img
            #display full img
            #firstLoad = False
        #if return 
            #if firstLoad == False
                #go to main

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
    draw_Radius = radius
    noting = True
    drawing_Start = time.monotonic() #Measure first time
    while noting == True:
        while tsc.touched:
            point = tsc.touch
            if point["pressure"] < 20: # ignore touches with no 'pressure' as false
                continue
            #yPos = int(point["y"]*yscale)
            #xPos = int(point["x"]*xscale)
            yPos = int((point["y"]*yscale))
            xPos = int(point["x"]*xscale)
            drawing_Start = time.monotonic() #New time measurement every time screen is touched
            if circleColor == colorBlack:
                drawImg.circle((xPos,yPos), draw_Radius, circleColor, circleColor, 1)
                #drawImg.putpixel((yPos,xPos),drawColor) # Edit image based on coordinates of points touched
            if circleColor == colorRed:
                drawImgRed.circle((xPos,yPos), draw_Radius, colorBlack, colorBlack, 1)
                #drawImgRed.putpixel((yPos,xPos),colorBlack) # Edit image based on coordinates of points touched
            if circleColor == colorWhite:
                drawImg.circle((xPos,yPos), draw_Radius, circleColor, circleColor, 1)
                drawImgRed.circle((yPos,xPos), draw_Radius, circleColor, circleColor, 1)
                #drawImg.putpixel((yPos,xPos),drawColor) # Edit image based on coordinates of points touched
                #drawImgRed.putpixel((yPos,xPos),colorBlack) # Edit image based on coordinates of points touched
        drawing_Stop = time.monotonic() - drawing_Start
        if drawing_Stop >= 1:
            noting = False
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
                    #Quick Save
                    if 98 >= xPos <= 160:
                        quicksave()
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

