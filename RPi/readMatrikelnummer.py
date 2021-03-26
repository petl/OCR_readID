##Script to read a photo from the raspberry camera and try to extract a Matrikelnummer
#9.2020 peter@traunmueller.net


from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageEnhance, ImageFilter
import pytesseract
from picamera import PiCamera
import time
from io import StringIO
import subprocess
import os
from datetime import datetime
import board
import busio
import digitalio
import adafruit_pcd8544
import threading
import requests
import re

# Motion detection settings
#how white an imgae has to be to be recognised as a TUcard
sensitivity = 100

# File settings
saveWidth = 360
saveHeight = 240
diskSpaceToReserve = 40 * 1024 * 1024 # Keep 40 mb free on disk

#LEDs
LED_white = digitalio.DigitalInOut(board.D17)
LED_white.switch_to_output()
LED_white.value = True
LED_green = digitalio.DigitalInOut(board.D18)
LED_green.switch_to_output()
LED_green.value = False
LED_red = digitalio.DigitalInOut(board.D23)
LED_red.switch_to_output()
LED_red.value = False

#LCD
BORDER = 5
FONTSIZE = 10
spi = busio.SPI(board.SCK, MOSI=board.MOSI)
dc = digitalio.DigitalInOut(board.D6)  # data/command
cs = digitalio.DigitalInOut(board.CE0)  # Chip select
reset = digitalio.DigitalInOut(board.D5)  # reset
display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)
display.bias = 4
display.contrast = 60
backlight = digitalio.DigitalInOut(board.D13)  # backlight
backlight.switch_to_output()
backlight.value = False #false is ON
display.fill(0)
display.show()
image = Image.new("1", (display.width, display.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

starttime = int(round(time.time() * 1000))

#the image taker and number reader
def readMatrikelnummer(filename):
    #camera.capture('1.jpg')
    #filename = "./photos/20210208-003515.jpg"
    print(filename)
    nowtime= int(round(time.time() * 1000))
    print("Ausweis gelesen. " )#+ str(nowtime-starttime))
    draw.text(
        (0, 10),
        "Ausweis gelesen.",
        font=font,
        fill=255,
    )
    draw.text(
        (0, 20),
        "Bitte rausziehen.",
        font=font,
        fill=255,
    )
    draw.text(
        (0, 30),
        "Bildanalyse",
        font=font,
        fill=255,
    )
    display.image(image)
    display.show()

    global blinkLEDsON #otherwise it would be a local variable with the same name
    blinkLEDsON = 1

    #is it a new TUCard ?
    im = Image.open(filename)
    print("Neuer Ausweis?")
    im1 = im.crop((40, 290, 260, 335)) #left, top, right, bottom    im1.save("1_nr.jpg")
    #blur filter
    #im1 = im1.filter(ImageFilter.BLUR)
    #im1 = im1.filter(ImageFilter.EDGE_ENHANCE)
    im1 = im1.filter(ImageFilter.MinFilter(3))
    #enhancer
    #enhancer = ImageEnhance.Contrast(im1)
    #factor = 3
    #im1 = enhancer.enhance(factor)
    im1.save("1_nr_neuerAusweis.jpg")
    #custom_config = r'-l TUcard --psm 7 --oem 1 outputbase digits'
    custom_config = r' --psm 7 --oem 1 outputbase digits'
    text = pytesseract.image_to_string(im1, config=custom_config)
    print(text)
    matrnr = re.match(r"([0-9]+)", text, re.I)
    if matrnr:
        matrnr = matrnr.groups()[0]
    else:
        matrnr = "0"
    if len(matrnr) < 7 or len(matrnr) > 8: #matrnr are between 7 and 8 digits
        matrnr = "0"
    print(matrnr)

    draw.text(
        (0, 30),
        "Bildanalyse...alt?",
        font=font,
        fill=255,
    )
    display.image(image)
    display.show()

    #is it an old TUCard ?
    if(matrnr == "0"):
        print("Alter Ausweis?")
        im1 = im.crop((400, 355, 620, 395)) #left, top, right, bottom
        #blur filter
        #im1 = im1.filter(ImageFilter.BLUR)
        #im1 = im1.filter(ImageFilter.EDGE_ENHANCE)
        im1 = im1.filter(ImageFilter.MinFilter(3))
        #enhancer
        #enhancer = ImageEnhance.Contrast(im1)
        #factor = 3
        #im1 = enhancer.enhance(factor)
        im1.save("1_nr_alterAusweis.jpg")

        text = pytesseract.image_to_string(im1, config=custom_config)
        print(text)

        matrnr = re.match(r"([0-9]+)", text, re.I)
        if matrnr:
            matrnr = matrnr.groups()[0]
        else:
            matrnr = "0"
        if len(matrnr) < 7 or len(matrnr) > 8: #matrnr are between 7 and 8 digits
            matrnr = "0"
        print(matrnr)

    #the numbers never start with a "4", but often "1" gets recognized as "4"
    if str(matrnr)[0] == "4":
        print("corrected a leading '4' to a '1'")
        matrnr = str(matrnr)
        matrnr = "1" + matrnr[1:]
    #print(matrnr)

    ##boxes = pytesseract.image_to_boxes('1.jpg', config=custom_config)
    #print(boxes)

    nowtime= int(round(time.time() * 1000))
    print("Hallo " + str(matrnr) + "!")# + str(nowtime-starttime))

    draw.rectangle((0,0,display.width,display.height), outline=0, fill=0) # clear image
    draw.text( (20, 10),"Hallo!",font=font,fill=255)
    draw.text( (20, 20),str(matrnr),font=font,fill=255)
    draw.text( (20, 30),"eingetragen",font=font, fill=255)
    display.image(image)
    display.show()
    blinkLEDsON = 0
    time.sleep(2)


    print("Formated MatrNr:"+str(matrnr))
    #return what we've done
    if len(matrnr) < 7 or len(matrnr) > 8: #matrnr are between 7 and 8 digits
        return 0
    else:
        return matrnr

def uploadData(filename, matrnr):
    print("Upload to server")
    url = 'https://quiescentcurrent.com/da/readerUpload/uploadFromPi.php'
    post_files = {'fileToUpload': open(filename, 'rb')}
    post_data = { 'MatrNr' :  matrnr}
    r = requests.post(url, data = post_data,  files=post_files)
    #print(r.text)

def blinkLEDs():
    while True:
        if blinkLEDsON == 1:
            LED_red.value = False
            LED_green.value = True
            time.sleep(0.2)
            LED_red.value = True
            LED_green.value = False
            time.sleep(0.2)


# Capture a small test image (for motion detection)
def captureTestImage():
    #command = "raspistill -w %s -h %s -t 0 -e bmp -o -" % (100, 75)
    #imageData = StringIO()
    #imageData.write(subprocess.check_output(command, shell=True))
    #imageData.seek(0)
    camera.capture('reference_Image.jpg')
    im = Image.open('reference_Image.jpg')
    im_compare = im.crop((560, 300, 600, 350)) #left, top, right, bottom
    im_compare.save("im_compare.jpg")
    buffer = im_compare.load()
    return im_compare, buffer

# Save a full size image to disk
def saveImage(width, height, diskSpaceToReserve):
    time = datetime.now()
    filename = "./photos/%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    camera.capture(filename)
    return filename
    #print("Captured %s" % filename)

def drawDefaultImage():
    draw.rectangle((0,0,display.width,display.height), outline=0, fill=0) # clear image
    draw.text( (0, 0),"-ANWESENHEIT-",font=font,fill=255)
    draw.text( (5, 15),"Neuen Ausweis",font=font,fill=255)
    draw.text( (15, 25),"einstecken",font=font,fill=255)
    draw.text( (20, 35),"--Peter--",font=font,fill=255)
    display.image(image)
    display.show()



text = "Setup ready!"
(font_width, font_height) = font.getsize(text)
drawDefaultImage()
#display.image(image)
#display.show()


 ##set up the camera
camera = PiCamera()
camera.rotation = 270
camera.resolution = (640,480)
camera.framerate = 30
camera.color_effects = (128,128)
camera.start_preview()
# Get first image
image1, buffer1 = captureTestImage()

# Reset last capture time
lastCapture = time.time()

#get an instance of the blinking leds for later
blinkLEDsThread = threading.Thread(target=blinkLEDs, args=())
blinkLEDsON = 0
blinkLEDsThread.start()

print("Setup fertig, bereit für Ausweise.")
LED_green.value = True

while (True):

    # Get comparison image
    image2, buffer2 = captureTestImage()

    #check how much white is in the image cutout
    #black==background
    #white==TUcard
    stat = ImageStat.Stat(image2)
    averageWhiteness = stat.mean[0]

    #print(averageWhiteness)

    if averageWhiteness > sensitivity:
        LED_green.value = False
        LED_red.value = True
        draw.rectangle((0,0,display.width,display.height), outline=0, fill=0) # clear image
        draw.text( (0, 0),"Lese Ausweis..",font=font,fill=255)
        display.image(image)
        display.show()
        print("Lese Ausweis..ruhig")
        lastCapture = time.time()
        filename = saveImage(saveWidth, saveHeight, diskSpaceToReserve)
        #filename = "./photos/20210209-133941.jpg"
        matrnr = readMatrikelnummer(filename)
        if matrnr != 0:
            uploadData(filename, matrnr)
        LED_green.value = True
        LED_red.value = False
        drawDefaultImage()
        print("Neuen Ausweis einstecken.")

    drawDefaultImage()

    # Swap comparison buffers
    image1 = image2
    buffer1 = buffer2
