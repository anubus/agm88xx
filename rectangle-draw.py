#  practice pillow rectangle drawing


import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735  # pylint: disable=unused-import
from colour import Color
import time



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

# set up color list array
COLORDEPTH = 1024
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

# create array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
# set for landscape mode
height = disp.width
width = disp.height

image = Image.new("RGB", (width, height))
print("Width: ", width)
print("Height: ", height)

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a box with rotating colors blue to red
while True:
    for i in range(COLORDEPTH -1):
        draw.rectangle((0, 0, width, height), fill=colors[i])
        disp.image(image)

