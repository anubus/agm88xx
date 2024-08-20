import busio
import board
import adafruit_amg88xx
from time import sleep

i2c_bus = busio.I2C(board.SCL, board.SDA)

sensor = adafruit_amg88xx.AMG88XX(i2c_bus)
sleep(0.1)

MINTEMP = 26.0 # low range of the sensor (this will be blue on the screen)
MAXTEMP = 32.0 # high range of the sensor (this will be red on the screen)
COLORDEPTH = 1024


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

print("orig")
print(sensor.pixels)

pixels = []
for row in sensor.pixels:
    pixels = pixels + row

print("new")
print(pixels)

pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]

print("mapped pixels")
print(pixels)

    