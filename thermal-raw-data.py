# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This example is for Raspberry Pi (Linux) only!
   It will not work on microcontrollers running CircuitPython!
port to display on adafruit tft display
"""

import os
import math
import time

import numpy as np
import pygame
import busio
import board

import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735  # pylint: disable=unused-import
from scipy.interpolate import griddata
from colour import Color
import adafruit_amg88xx

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()
i2c_bus = busio.I2C(board.SCL, board.SDA)

disp = st7735.ST7735R(spi, rotation=90,      # 1.8" ST7735R
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)
# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.

if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a green filled box as the background
draw.rectangle((0, 0, width, height), fill=(0, 255, 0))
disp.image(image)


MINTEMP = 26.0 # low range of the sensor (this will be blue on the screen)
MAXTEMP = 32.0 # high range of the sensor (this will be red on the screen)

# how many color values we can have
COLORDEPTH = 1024

#os.putenv("SDL_FBDEV", "/dev/fb1")
pygame.init()

# initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# initial stuff for bicubic
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

# sensor is an 8x8 grid so lets do a square
height = 240
width = 240

# the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

# create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

lcd = pygame.display.set_mode((width, height))
'''
lcd.fill((255, 0, 0))

pygame.display.update()
pygame.mouse.set_visible(False)
'''
lcd.fill((0, 0, 0))
pygame.display.update()


# some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# let the sensor initialize
time.sleep(0.1)

while True:
    # read the pixels
    pixels = []
    for row in sensor.pixels:    # gets rid of rows and makes a single list of pixel values
        pixels = pixels + row
    pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
    print("Mapped pixels")
    print("Size of pixels list = ", len(pixels))
    print(pixels)
    # perform interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")
    print("Interpolated")
    print("shape = ", bicubic.shape)
    with np.printoptions(threshold=np.inf):
        print(bicubic)
    # draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            pygame.draw.rect(
                lcd,
                colors[constrain(int(pixel), 0, COLORDEPTH - 1)],
                (
                    displayPixelHeight * ix,
                    displayPixelWidth * jx,
                    displayPixelHeight,
                    displayPixelWidth,
                ),
            )

    pygame.display.update()
    disp.image(image)
    time.sleep(5)

