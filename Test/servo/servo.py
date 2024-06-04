import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.OUT)
servo1 = GPIO.PWM(12, 50) # GPIO 12 for PWM with 50Hz

servo1.start(0)

servo1.ChangeDutyCycle(2)
time.sleep(2)
servo1.ChangeDutyCycle(0)

pressing_time = int(input("Enter servo time: "))
button_angle = float(input("Enter servo angle: "))
pressing_duration = float(input("Enter servo duration: "))

for i in range(pressing_time):
    print(f"Pressing button", i+1, "time")
    angle = button_angle
    angle2duty = 2+((angle/180)*10)
    servo1.ChangeDutyCycle(angle2duty)
    time.sleep(pressing_duration)
    angle = 0
    angle2duty = 2+((angle/180)*10)
    servo1.ChangeDutyCycle(angle2duty)
    time.sleep(0.5)

servo1.stop()
GPIO.cleanup()
print("Servo stopped")
