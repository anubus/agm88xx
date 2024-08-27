#  practice pillow rectangle drawing


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

# Setup I2C bus 
i2c_bus = busio.I2C(board.SCL, board.SDA)

# initialize amg88 sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)
time.sleep(0.5)  # time for sensor to initialize

# set up color list array
COLORDEPTH = 1024
blue = Color("indigo")
red = Color("red")
#colors = list(blue.range_to(Color("red"), COLORDEPTH))
colors = list(red.range_to(Color("indigo"), COLORDEPTH))

# set temperature range
MINTEMP = 25.0  # low range, blue on screen (sensor min = 0c)
MAXTEMP = 30.0  # high range, red on screen (sensor max = 80c)

# set up temperature scale
LEGENDBORDER = 129
SCALESTEP = 10
scale = np.linspace(MINTEMP, MAXTEMP, SCALESTEP)
colorScale = np.linspace(0, COLORDEPTH - 1, SCALESTEP)
print(scale, colorScale)
for t in scale:
    print(round(t, 1))
for c in colorScale:
    print(int(c))
    print(colors[int(c)])

# load fonts for use in scale display
FONTSIZE = 10
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

# create array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
# this display is landscape oriented so swap height/width
height = disp.width  # 160
width = disp.height  # 128
image = Image.new("RGB", (width, height))

print(" Display width: ", width)
print("         height: ", height)

# sensor display window, maximum square to fit display
displayPixel =  4   # sensor is 8 x 8

# utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map_value(x, in_min, in_max, out_min, out_max):
    return(x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

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
text = str(round(MAXTEMP, 1))
for lx, temp in enumerate(scale):
    text = str(round(temp, 1))
    (font_x, font_y, font_width, font_height) = font.getbbox(text)
    draw.text(
        (width - font_width, height - lx * height // font_height - height // font_height),
        text,
        font = font,
        fill = (255, 255, 255),
    )

# Draw a box with rotating colors blue to red
while True:
    # read the sensor pixels
    pixels = []
    for row in sensor.pixels:    # gets rid of rows and maks a single list of pixel values
        pixels = pixels + row
    pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH -1) for p in pixels]
    # interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method = "cubic")
    # draw it
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            draw.rectangle(
                    (
                        displayPixel * ix,
                        displayPixel * jx,
                        displayPixel * ix + displayPixel,
                        displayPixel * jx + displayPixel
                    ),
                    fill = colors[constrain(int(pixel), 0, COLORDEPTH -1)]
            )
    disp.image(image)

