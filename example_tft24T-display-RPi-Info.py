# tft24T    V0.2 April 2015     Brian Lavery    TJCTM24024-SPI    2.4 inch Touch 320x240 SPI LCD
# example-tft24T-display-RPi-Info.py            Franz Heinzl

#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

# This program  allows to use Python code to show some Linux statistics on the attached display

"""
It is required to enable SPI on your platform. Check with:    ls /dev/spi*
Should show response:                                         /dev/spidev0.0   /dev/spidev0.1

Install the Raspberry PI GPIO library:
pip3 install RPI.GPIO

Install spidev for SPI interfacing

Raspberry Pi usually comes with the DejaVu font already installed:
sudo apt-get install ttf-dejavu

PIL (Pillow library), the Python Imaging Library, is needed to allow graphics and using text with custom fonts.
sudo apt-get install python3-pil
"""

#PINOUT:
# 3.3v - connected to display VCC
# GND  - connected to display GND
# SCK, MOSI, CE0
# MISO - not needed to display because it is in input pin (e.g. SD card, touch)
# DC   - any free GPIO pin


from PIL import Image, ImageDraw, ImageFont
from lib_tft24T import TFT24T
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD) # Pins to be defined according to P1 pinout of the board
GPIO.setwarnings(False)

import spidev
import subprocess  # to gather some system information
from time import sleep  # to add small delays between the display updates


# Raspberry Pi configuration for TFT screen.
DC = 15  # pin 15 on P1 pin out is the same as GPIO22
# RST pin connected to +3.3V
# LED pin connected to +3.3V
SPI = spidev.SpiDev()  # setup SPI bus using hardware SPI.

# Create TFT object:
TFT = TFT24T(SPI, GPIO, landscape=True)  # If landscape=False or omitted, display defaults to portrait mode

# Initialize display.
# TFT.initLCD(DC, RST, LED)
TFT.initLCD(DC)

# Get the PIL Draw object to start drawing on the display buffer.
draw = TFT.draw()

# Define the font
# font = ImageFont.load_default()
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# Constants for positing of text.
padding = -2
x = 0

while True:
    draw.rectangle((0, 0, 240, 320), outline=0, fill="black")

    # Shell scripts for system monitoring:
    # Using the subprocess function that get called to the Operating System to get information.
    # Then each command is passed through awk in order to be formated better for the display.
    # By having the OS do the work, we don't have to.
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d' ' -f1"
    IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "top -bn1 | grep load |tr ',' '.' | awk '{printf \"CPU Load: %.4s%%\", $(NF-2)*100}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Tem: %.1f C\", $(NF-0) / 1000}'"
    Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")    
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # Write four lines of text:
    y = padding
    draw.text((x, y), IP, font=font, fill="White")
    y += font.getsize(IP)[1] + 2
    draw.text((x, y), CPU, font=font, fill="Yellow")
    y += font.getsize(CPU)[1] + 2
    draw.text((x, y), Temp, font=font, fill="Red")
    y += font.getsize(Temp)[1] + 2
    draw.text((x, y), MemUsage, font=font, fill="Green")
    y += font.getsize(MemUsage)[1] + 2
    draw.text((x, y), Disk, font=font, fill="Blue")
    y += font.getsize(Disk)[1] + 5

    # Write small image to canvas:
    draw.pasteimage("rpi3.jpg", (245, 0))  # custom method for coloured image

    # Display image:
    TFT.display()
    sleep(0.5)


#        All colours may be any notation (exc for clear() function):
#        (255,0,0)  =red    (R, G, B) - a tuple
#        0x0000FF   =red    BBGGRR   - note colour order
#        "#FF0000"  =red    RRGGBB   - html style
#        "red"      =red    html colour names, insensitive
