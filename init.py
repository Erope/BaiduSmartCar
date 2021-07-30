import time
import getpass
import os
from control.action import Set_Flag, Set_Catch, Set_Down, Set_Dump_Ball
from motor.i2c import motor
import cv2
import serial.tools.list_ports

port = '/dev/ttyS0' # 舵机
sp = serial.Serial(port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
             xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=0, dsrdtr=False)

def i2cdetect():
    cmd = '''i2cdetect -a -y 1 0x01 0x04 | grep "01 02 03 04"'''
    return os.system(cmd)

def motor_detect():
    motor().detect()

def camera_detect():
    cap = cv2.VideoCapture(0)
    #cap.set(cv2.CAP_PROP_FOURCC, 1196444237)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    time.sleep(0.5)
    if int(cap.get(cv2.CAP_PROP_FPS)) != 30:
        cap.release()
        return False
    ret, _ = cap.read()
    if not ret:
        cap.release()
        return False
    cap.release()
    return True

def openmv_detect():
    sp_s = serial.tools.list_ports.grep('/dev/mv_(\d)', include_links=True)
    if len(list(sp_s)) != 2:
        return False
    for i in sp_s:
        if i[0] != '/dev/mv_0' and i[0] != '/dev/mv_1':
            return False
    return True

def machine_init():
    # 舵机初始化
    Set_Flag(0)
    time.sleep(0.1)
    Set_Down(0)
    time.sleep(0.1)
    Set_Catch(0)
    time.sleep(0.1)
    Set_Dump_Ball(0)
    time.sleep(1)

def init():
    # 初始化程序，用于程序运行刚开始时候初始程序以及诊断
    # 判断权限
    assert getpass.getuser() == "root"
    # 判断电机i2c是否在线
    assert i2cdetect() == 0
    time.sleep(0.1)
    # 电机蜂鸣
    motor_detect()
    time.sleep(0.1)
    # 摄像头诊断
    assert camera_detect()
    # OpenMV诊断
    assert openmv_detect()
    # 舵机初始化
    machine_init()
    return True

if __name__ == '__main__':
    init()
