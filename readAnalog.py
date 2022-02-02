import RPi.GPIO as GPIO
import time

# declare GPIO mode
GPIO.setmode(GPIO.BCM)

# define GPIO pins with variables charge_pin and measure_pin
# 18=chargepin 23=measure
charge_pin=18
measure_pin =

# discharge the capacitor
def discharge():
    GPIO.setup(charge_pin, GPIO.IN) #stop charging
    GPIO.setup(measure_pin, GPIO.OUT) #make the measure pin an output
    GPIO.output(measure_pin, False) # set it low to discharge the capacitor
    time.sleep(0.005)

def charge_time():
    GPIO.setup(measure_pin, GPIO.IN)
    GPIO.setup(charge_pin, GPIO.OUT)
    count = 0
    GPIO.output(charge_pin, True) #start charging the capacitor
    while not GPIO.input(measure_pin): #wait till the pin goes HIGH
        count = count +1
    return count

def analog_read():
    discharge()
    return charge_time()

# loop to display analog data count
while True:
    print(analog_read())
    time.sleep(1)
