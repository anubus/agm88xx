# test python gpio testing

import time
import digitalio
import board

led = digitalio.DigitalInOut(board.D21)
led.direction = digitalio.Direction.OUTPUT
while True:
    led.value = True
    time.sleep(0.1)
    led.value = False
    time.sleep(0.1)
