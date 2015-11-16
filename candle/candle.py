#!/usr/bin/env python

# Import the modules used in the script
import random, time
import RPi.GPIO as GPIO

# Assign the hardware PWM pin and name it

class LED(object):
    def __init__(self, gpio):
        self.gpio = gpio
        self.brightness = [0, 0]
        GPIO.setup(gpio, GPIO.OUT)
        self.pwm = GPIO.PWM(gpio, 100)
        self.pwm.ChangeFrequency(100)
        self.pwm.start(0)

    def pop(self):
        return self.brightness.pop(0)

led_gpio = [18, 17, 27, 22, 23]

# Configure the GPIO to BCM and set it to output mode
GPIO.setmode(GPIO.BCM)
leds = [LED(gpio=i) for i in led_gpio]

# Set PWM and create some constants we'll be using

RUNNING = True
wind = 9

def brightness():
    """Function to randomly set the brightness of the LED between 5 per cent and 100 per cent power"""
    return random.randint(5, 100)

def flicker():
    """Function to randomly set the regularity of the'flicker effect'"""
    return random.random() / wind

print "Candle Light. Press CTRL + C to quit"

# The main program loop follows.
# Use 'try', 'except' and 'finally' to ensure the program
# quits cleanly when CTRL+C is pressed to stop it.


wind_counter = 0
wind_duration = 100

def last80(last_bright, last_led):
    return last_bright * 0.80

def last60(last_bright, last_led):
    return last_bright * 0.60

def last40(last_bright, last_led):
    return last_bright * 0.40

def last20(last_bright, last_led):
    return last_bright * 0.20

def pop80(last_bright, last_led):
    return last_led.pop() * 0.80

def pop60(last_bright, last_led):
    return last_led.pop() * 0.60

def pop40(last_bright, last_led):
    return last_led.pop() * 0.40

def pop20(last_bright, last_led):
    return last_led.pop() * 0.20

def off(last_bright, last_led):
    return 0

def base(last_bright, last_led):
    return random.randint(5, 100)


next_brighness_matrix = [
    [base] * len(leds),
    [last80, last80, last80, last80, last20],
    [last60, last40,  last20,  off,  off],
    [last40, last20,  off,  off,  off],
    [last40, off,    off,    off,  off]
]

##next_brighness_matrix = [
##    [base] * len(leds),
##    [last80, last80, last80, pop80, pop20],
##    [pop60, pop40,  pop20,  off,  off],
##    [last40, pop40,  off,  off,  off],
##    [pop40, off,    off,    off,  off]
##]
##

def run():
    global wind_counter
    global wind_duration
    global wind

    previous_bright = 0
    previous_led = leds[0]

    activity = 32

    while RUNNING:

        random_activity = random.randint(0, 4)
        if random_activity == 0:
            activity -= 1
        elif random_activity == 1:
            activity += 1
        if random_activity > 32:
            random_activity = 16
        elif random_activity < 0:
            random_activity = 16


        wind_counter += 1
        if wind_counter > wind_duration:
            wind = random.randint(2, 4)
            wind_counter = 0
            wind_duration = 250 / (5 - wind)
            print "w ", wind
        # Start PWM with the LED off

        # Randomly change the brightness of the LED
        for i, led in enumerate(leds):
##            if i == 0:
##                b = brightness()
##            else:
##                level_rand = random.randint(0, len(leds) * 2)
##                if level_rand < i - 1:
##                    b = previous_led.brightness.pop(0) * 0.75
##                elif level_rand < i * 2:
##                    b = 0
##                    previous_led.brightness.pop(0)
##                else:
##                    b = int(previous_bright * 0.55)
##                    previous_led.brightness.pop(0)

            led_control = next_brighness_matrix[i]
            try:
                next_level_fn = led_control[random.randint(0, activity)]
            except (IndexError, ValueError):
                next_level_fn = led_control[-1]
            b = next_level_fn(previous_bright, previous_led)

            previous_bright =  b
            previous_led = led
            print i, b
            led.pwm.start(0)
            led.brightness.append(b)
            led.pwm.ChangeDutyCycle(b)
            # Randomly pause on a brightness to simulate flickering
        f = flicker()
        time.sleep(f)

try:
    while True:
        try:
            run()
            # If CTRL+C is pressed the main loop is broken
        except KeyboardInterrupt:
            running = False
            print "pause"
            time.sleep(10.0)




# Actions under 'finally' will always be called, regardless of
# what stopped the program (be it an error or an interrupt)
finally:
    # Stop and cleanup to finish cleanly so the pins
    # are available to be used again
    for an_led in leds:
        an_led.pwm.stop()
    GPIO.cleanup()

