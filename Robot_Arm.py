import RPi.GPIO as GPIO
import ADC0834
import time

# define gpio pins
claw = 5
# currently the vertical movement servo is unused because the analog stick
# only has x, y inputs and a button input
vert = 6
horz = 12
rot = 13
button = 22
# use list for multiple GPIO outputs
chan_list = (claw, vert, horz, rot, button)

# must use BCM here because that is the mode used in ADC0834.py
GPIO.setmode(GPIO.BCM)

lastX = 0
lastY = 0
lastBtn = 1

# prepare input from analog stick pin
# x axis 0-129-255, where 129=default
# y axis 0-127-255, where 127=default
# button 0-1, where 1=default, 0=click
def setupInput():
    GPIO.setup(button, GPIO.IN)
    ADC0834.setup()

# prepare output to servo motor pins
def setupOutput():
    GPIO.setup(claw, GPIO.OUT)
    GPIO.setup(vert, GPIO.OUT)
    GPIO.setup(horz, GPIO.OUT)
    GPIO.setup(rot, GPIO.OUT)
    global clawPwm
    global vertPwm
    global horzPwm
    global rotPwm
    clawPwm = GPIO.PWM(claw, 50)
    vertPwm = GPIO.PWM(vert, 50)
    horzPwm = GPIO.PWM(horz, 50)
    rotPwm = GPIO.PWM(rot, 50)
    clawPwm.start(0)
    vertPwm.start(0)
    horzPwm.start(0)
    rotPwm.start(0)

# mapping function similar to arduino's built in map function, 
# taking x value in a certain range and converting it to a new range
def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# set angles of servo motors in robot arm according to input of analog stick
def setAngles(xAngle, yAngle, button):
    global lastX, lastY, lastBtn
    if abs(lastX - xAngle) > 1:
        horzPwm.ChangeDutyCycle(xAngle)
    clawPwm.ChangeDutyCycle(button)
    if abs(lastY - yAngle) > 0:
        rotPwm.ChangeDutyCycle(yAngle)
    time.sleep(.25)
    horzPwm.ChangeDutyCycle(0)
    rotPwm.ChangeDutyCycle(0)
    clawPwm.ChangeDutyCycle(0)
    lastX = xAngle
    lastY = xAngle
    lastBtn = button

# release resources
def destroy():
    clawPwm.stop()
    vertPwm.stop()
    horzPwm.stop()
    rotPwm.stop()
    GPIO.cleanup()

# loop for input from analog stick, converting it using the ADC0834 library, 
# remap it to PWM range and output to servo motors of arm
def loop():
    while True:
        x_val = ADC0834.getResult(0)
        y_val = ADC0834.getResult(1)
        btn_val = GPIO.input(button)
        print('X: %d  Y: %d  Btn: %d' % (x_val, y_val, btn_val))
        xMappedInput = _map( x_val, 0, 255, 2, 12)
        yMappedInput = _map( y_val, 0, 255, 2, 12)
        btnMappedInput = _map( btn_val, 0, 1, 10, 13)
        print(x_val, y_val, btnMappedInput)
        setAngles(xMappedInput, yMappedInput, btnMappedInput)


if __name__ == '__main__':
    setupInput()
    setupOutput()
    try:
        loop()
    except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the program destroy() will be executed.
        destroy()
		
	
