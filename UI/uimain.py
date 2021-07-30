import scipy as sp
from .display import lcd
import RPi.GPIO as GPIO
from .config import *
from init import machine_init

import time
dis = lcd()
status = 0
speed_sel = 0
CarStatus = None

use_flag = []
base_speed = None
angle_speed = None
x_speed = None
y_speed_change = None
AngleChange = None
CityList = None
Flag_Run = None

def gpio_setup():
    # GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
    # GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
    # GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
    GPIO.setup(KEY_List, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.setup(BUTTON_List, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in KEY_List:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=key_down, bouncetime=200)
    for pin in BUTTON_List:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=but_down, bouncetime=130)

def key_down(channel):
    key_num = KEY_List.index(channel)
    print(f"{key_num} is down...")
    global status, speed_sel, angle_speed, base_speed, x_speed, CarStatus, CityList
    if status == 0:
        if key_num == 3:
            if CarStatus.value == -1:
                CarStatus.value = 0
            else:
                CarStatus.value = -1
        if key_num == 4:
            machine_init()
    elif status == 1:
        if key_num < 3:
            city_name = Key_City[key_num]
            if city_name not in use_flag and len(use_flag) <= 3:
                use_flag.append(city_name)
                CityList[len(use_flag) - 1] = key_num
        elif key_num == 3:
            if len(use_flag) == 3:
                status = 0
        elif key_num == 4:
            use_flag.clear()
            for i in range(0, 3):
                CityList[i] = i
            status = 0
    elif status == 2:
        if key_num == 0:
            if speed_sel == 4:
                speed_sel = 0
            else:
                speed_sel += 1
        elif key_num == 1:
            if speed_sel == 1:
                angle_speed.value += speed_step
            elif speed_sel == 0:
                base_speed.value += speed_step
            elif speed_sel == 2:
                x_speed.value += speed_step
            elif speed_sel == 3:
                y_speed_change.value += speed_step
            elif speed_sel == 4:
                AngleChange.value += speed_step
        elif key_num == 2:
            if speed_sel == 1:
                angle_speed.value = max(angle_speed.value - speed_step, 0)
            elif speed_sel == 0:
                base_speed.value = max(base_speed.value - speed_step, 0)
            elif speed_sel == 2:
                x_speed.value = max(x_speed.value - speed_step, 0)
            elif speed_sel == 3:
                y_speed_change.value = max(y_speed_change.value - speed_step, 0)
            elif speed_sel == 4:
                AngleChange.value = max(AngleChange.value - speed_step, 0)
        else:
            status = 0
    elif status == 3:
        if key_num <= 2:
            if Flag_Run[key_num] == 0:
                Flag_Run[key_num] = 1
            else:
                Flag_Run[key_num] = 0
        elif key_num == 3:
            CarStatus.value = 4
            status = 0
        else:
            status = 0
    menu()

def but_down(channel):
    but_num = BUTTON_List.index(channel)
    print(f"{but_num} is down...")
    global status
    status = but_num + 1
    if status == 1:
        use_flag.clear()
    menu()

def menu():
    global sel, status
    if status == 0:
        status_list = []
        if len(use_flag) == 3:
            flag_str = ""
            for flag in use_flag:
                flag_str += flag[0:1] + " "
            status_list.append(flag_str)
        else:
            status_list.append("旗帜未选择")
        status_list.append(f"基: {base_speed.value} 角: {angle_speed.value}")
        status_list.append(f"横: {x_speed.value} 基倍:{y_speed_change.value}")
        status_list.append(f"角倍:{AngleChange.value}")
        status_list.append(Status[CarStatus.value])
        dis.display(menu_main + status_list)
    elif status == 1:
        if len(use_flag) < 3:
            dis.display(menu_flag + use_flag + ["请选择"])
        else:
            dis.display(menu_flag + use_flag + ["请确认"])
    elif status == 2:
        if speed_sel == 1:
            status_list = ["选择: 角速度"]
            red_line = 3
        elif speed_sel == 0:
            status_list = ["选择: 基速度"]
            red_line = 2
        elif speed_sel == 2:
            status_list = ["选择: 横速度"]
            red_line = 4
        elif speed_sel == 3:
            status_list = ["选择: 基倍率"]
            red_line = 5
        elif speed_sel == 4:
            status_list = ["选择: 角倍率"]
            red_line = 6
        status_list += [f"基速: {base_speed.value}", f"角速: {angle_speed.value}", f"横速: {x_speed.value}", f"基倍: {y_speed_change.value}", 
                                f"角倍: {AngleChange.value}"]
        dis.display(menu_speed + status_list, red_line)
    elif status == 3:
        status_list = [f"靶子1: {Flag_Run[0]}", f"靶子2: {Flag_Run[1]}", f"靶子3: {Flag_Run[2]}",]
        dis.display(menu_special_run + status_list)

def showui(Car_Status, LinerSpeed, AngularSpeed, XSpeed, YSpeedChange, AngleChangeRate, City_List, FlagRun):
    global base_speed, angle_speed, x_speed, CarStatus, y_speed_change, AngleChange, CityList, Flag_Run
    CarStatus = Car_Status
    base_speed = LinerSpeed
    angle_speed = AngularSpeed
    y_speed_change = YSpeedChange
    x_speed = XSpeed
    AngleChange = AngleChangeRate
    CityList = City_List
    Flag_Run = FlagRun
    # print(type(base_speed))
    gpio_setup()

    while True:
        try:
            time.sleep(0.3)
            menu()
            pass
        except KeyboardInterrupt:
            break
    GPIO.cleanup()
