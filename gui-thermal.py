# initial thermal camera using pillow for display


import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735  # pylint: disable=unused-import
import adafruit_amg88xx
from colour import Color
import time
from  scipy.interpolate import griddata
import numpy as np
import math
import busio


# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()
disp = st7735.ST7735R(spi, rotation=90,                           # 1.8" ST7735R
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# initialize amg88 sensor
i2c_bus = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)
time.sleep(0.5)  # time for sensor to initialize

# option to show temps in fahrenheit
fahrenheit = True

# set up color list array
COLORDEPTH = 1024
blue = Color("indigo")
red = Color("red")
#colors = list(blue.range_to(Color("red"), COLORDEPTH))
colors = list(red.range_to(Color("indigo"), COLORDEPTH))

# set temperature range
minTemp = 26.0  # low range, blue on screen (sensor min = 0c)
maxTemp = 40.0  # high range, red on screen (sensor max = 80c)

# set up temperature scale
LEGENDBORDER = 129
SCALESTEP = 10
scale = np.linspace(minTemp, maxTemp, SCALESTEP)
colorScale = np.linspace(0, COLORDEPTH - 1, SCALESTEP)

# load fonts for use in scale display
FONTSIZE = 10
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

# create array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

# Create blank image for drawing with RGB colors
# this display is landscape oriented so swap height/width
height = disp.width  # 160
width = disp.height  # 128
image = Image.new("RGB", (width, height))

# sensor display window, maximum square to fit display
# square display area 128 pixels on a side
# sensor is 8 x 8 interpolated to 32 x 32
displayPixel =  4   # 4 x 32 = 128

# utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map_value(x, in_min, in_max, out_min, out_max):
    return(x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def toF(celsius):     #convert celsius to fahrenheit
    return(celsius * 1.8) + 32

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# inialize bicubic stuff
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

#display color legend scale stripe
for kx, legendColor in enumerate(colorScale):
    draw.rectangle(
            (
                LEGENDBORDER, 
                height - kx * height // SCALESTEP - height // SCALESTEP,
                width,
                height - kx * height // SCALESTEP + height // SCALESTEP - height // SCALESTEP
            ),
            fill = colors[int(legendColor)]
    )

# display scale numbers
for lx, temp in enumerate(scale):
    if fahrenheit:
        temp = toF(temp)
    text = str(round(temp, 1))
    (font_x, font_y, font_width, font_height) = font.getbbox(text)
    draw.text(
        (width - font_width, height - lx * height // font_height - height // font_height),
        text,
        font = font,
        fill = (255, 255, 255),
    )

# parameters for aiming circle at center of display
center = height // 2
circleSize = 5
offset = height // 8  # put aiming circle over sensor pixel closest to center (pixel 35)

# draw and update the displqy 
while True:
    # read the sensor pixels
    pixels = []
    for row in sensor.pixels:    # gets rid of rows and makes a single list of pixel values
        pixels = pixels + row
    centerPixel = pixels[35]
    pixels = [map_value(p, minTemp, maxTemp, 0, COLORDEPTH -1) for p in pixels]
    # interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method = "cubic")
    # draw it
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            draw.rectangle(
                    (
                        height - displayPixel * ix,                #subtract to mirror display
                        displayPixel * jx,
                        height - displayPixel * ix - displayPixel, #subtract to mirror display
                        displayPixel * jx + displayPixel
                    ),
                    fill = colors[constrain(int(pixel), 0, COLORDEPTH -1)]
            )
    # draw aiming center circle
    draw.ellipse((center -offset - circleSize, center - offset - circleSize, center - offset + circleSize, center - offset + circleSize), fill=None, outline=(255,255,255), width=2)
    if fahrenheit:
        pointTemp = toF(centerPixel)
        pointTemp = str(round(pointTemp,1)) + "\u00b0 F"
    else: 
        pointTemp = str(round(centerPixel,1)) + "\u00b0 C"
    draw.text((25, 25), pointTemp, font=font, fill=(255,255,255))
    # write the image to the display
    disp.image(image)

