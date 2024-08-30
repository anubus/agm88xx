# test python gpio testing

import time
import digitalio
import board

led = digitalio.DigitalInOut(board.D21)
led.direction = digitalio.Direction.OUTPUT
buttonLL = digitalio.DigitalInOut(board.D26)
buttonUL = digitalio.DigitalInOut(board.D19)
buttonLR = digitalio.DigitalInOut(board.D13)
buttonUR = digitalio.DigitalInOut(board.D6)
buttonLL.direction = digitalio.Direction.INPUT
buttonUL.direction = digitalio.Direction.INPUT
buttonLR.direction = digitalio.Direction.INPUT
buttonUR.direction = digitalio.Direction.INPUT
buttonLL.pull = digitalio.Pull.UP
buttonUL.pull = digitalio.Pull.UP
buttonLR.pull = digitalio.Pull.UP
buttonUR.pull = digitalio.Pull.UP

def blink():
    led.value = True
    time.sleep(0.3)
    led.value = False

print("Button test")

while True:
    if buttonLL.value == False:
        print("Lower Left button pressed!")
        blink()
 
    if buttonUL.value == False:
        print("Upper Left button pressed!")
        blink()
 
    if buttonLR.value == False:
        print("Lower Right button pressed!")
        blink()
 
    if buttonUR.value == False:
        print("Uper Right button pressed!")
        blink()
 
 

    
