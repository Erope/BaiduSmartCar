from motor.i2c import motor
import time

motor_dev = motor()
motor_dev.run([20, 20, 20, 20])
time.sleep(5)
motor_dev.run([0,0,0,0])