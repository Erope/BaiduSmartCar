import multiprocessing as mp
from multiprocessing import Process, Value, Array
import time
from UI.uimain import showui
from opencv.main import cv
from motor.main import line_run
from config import *
from control.maincontrol import CarControlRun, FlagRun
from init import init

if __name__ == '__main__':
    # 图像共享队列
    img_res_q = mp.Queue()
    # 动态共享参数值
    # 状态
    CarStatus = Value('i', -1) # Car状态 -1 停止 0 主控接管 1 巡线 2 校准 3 执行任务
    LinerSpeed = Value('i', conf_base_speed) # UI与Motor共享
    AngularSpeed = Value('i', conf_angle_speed) # UI与Motor共享
    XSpeed = Value('i', conf_X_speed)
    YSpeedChangeRate = Value('i', conf_Y_Change_speed)
    AngleChangeRate = Value('i', conf_Angle_Change_speed)
    CityList = Array('i', range(3)) # 1 2 3
    Flag_Run = Array('i', [1] * 3)

    print("正在启动初始化既诊断程序...")
    init()

    print("正在启动主程序...")
    ui_p = Process(target=showui, args=(CarStatus, LinerSpeed, AngularSpeed, XSpeed, YSpeedChangeRate, AngleChangeRate, CityList, Flag_Run))
    ui_p.start()
    cv_p = Process(target=cv, args=(img_res_q, XSpeed))
    cv_p.start()
    line_p = Process(target=line_run, args=(img_res_q, CarStatus, LinerSpeed, AngularSpeed, XSpeed, YSpeedChangeRate, AngleChangeRate))
    line_p.start()
    time.sleep(0.5)
    control_p = Process(target=CarControlRun, args=(CarStatus,CityList,Flag_Run))
    control_p.start()
    ui_p.join()
    cv_p.join()
    line_p.join()
    control_p.join()
