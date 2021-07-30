import numpy as np
from sklearn.linear_model import LinearRegression
import time
from .i2c import motor
from config import car_center

# 底盘长宽
a = 24 
b = 24
ChangeLimit = 5
AngleChangeLimit = 5
# 基础速度，最大速度，最小速度
LinerSpeed = None
MaxLinerSpeed = 30
# MinLinerSpeed = 10
# 基础角速度,最大角速度，最小角速度
AngularSpeed = None
XSpeed = None
YSpeedRate = None
AngleRate = None
# MaxAngularSpeed = 1
# MinAngularSpeed = 0.01
# 四个轮子的默认速度
# speed = [LinerSpeed.value,LinerSpeed.value,LinerSpeed.value,LinerSpeed.value]
# 传入x速度，y的速度，方向速度，传回四个轮子的转速
def mecanumRun(xSpeed,ySpeed,aSpeed):
    aSpeed = float(aSpeed)
    speed1 = ySpeed - xSpeed + aSpeed 
    speed2 = ySpeed + xSpeed - aSpeed
    speed3 = ySpeed - xSpeed - aSpeed
    speed4 = ySpeed + xSpeed + aSpeed
    # 倘若溢出则进行对应的归一化
    list_speed = [speed1,speed2,speed3,speed4]
    list_speed_p = []
    for i in list_speed:
        list_speed_p.append(abs(int(i)))
    max_speed = max(list_speed_p)
    if abs(int(max_speed)) > abs(int(MaxLinerSpeed)):
        speed1 = speed1 / max_speed * MaxLinerSpeed
        speed2 = speed2 / max_speed * MaxLinerSpeed
        speed3 = speed3 / max_speed * MaxLinerSpeed
        speed4 = speed4 / max_speed * MaxLinerSpeed
        list_speed = [speed1,speed2,speed3,speed4]
    return list_speed

# speed = mecanumRun(0,100,100)
# 于是乎，根据上面的函数有了，我们需要通过视频的返回值，获得一个xSpeed，ySpeed,转向角
# 在后续调试中，首先得定义上限速度，均速等，然后定义修改自转角速度
# 其中 aSpeed = (a+b)*angularspeed


# 方案1
# 现在有一个60*80的界面
# 以x = 40为中线，输入的点，其求角度
# 示例 print(angular([0,40]))
def angular(point_3, point_down):
    # 如果说
    a = point_3[1] - point_down[1]
    if a == 0:
        return 0
    b = point_3[0] - point_down[0]
    Angular=np.degrees(np.arctan(b/a))
    return Angular

# test

def LRgression(list_x, list_y):
    x = np.array(list_x).reshape(-1,1)
    y = np.array(list_y).reshape(-1,1)
    model = LinearRegression()
    model.fit(x, y)
    predict_y = model.predict(x)
    return predict_y # 可修改，与传入的数组串数据有关

# now_time = time.time()
# print(now_time)
# print(LRgression(list_x,list_y))
# print((time.time() - now_time) * 1000 )

# 传入拟合中线对应的部分参数坐标，这里以传入60*80中，纵坐标10~50共40个数据
def CarRun(x,y):
    # 根据仿真的值，选出对应的中心代表点
    predict_y = LRgression(y,x)
    center_point = predict_y[int(len(x) / 2 - 1)]
    low_point = predict_y[0]
    # print(center_point)
    # 根据目标中心点，得出目标偏转角度
    target_angular = angular((center_point, int(len(x) / 2 - 1)), (low_point, 0))
    #print(f"偏移{target_angular}")
    if abs(int(target_angular)) > ChangeLimit:
        x = x[0:int(len(x) * 1.0 / 2.0)]
        y = y[0:int(len(y) * 1.0 / 2.0)]
        predict_y = LRgression(y,x)
        center_point = predict_y[int(len(x) / 2 - 1)]
        low_point = predict_y[0]
        # print(center_point)
        # 根据目标中心点，得出目标偏转角度
        target_angular = angular((center_point, int(len(x) / 2 - 1)), (low_point, 0))
        if target_angular >= AngleChangeLimit:
            aSpeed = (a+b)*(AngularSpeed.value / 10000.0)*target_angular*(AngleRate.value / 100.0)
        else:
            aSpeed = (a+b)*(AngularSpeed.value / 10000.0)*target_angular
        #得出目标速度
        #print(f"中心{x[0]}")
        Target_Speed = mecanumRun(((car_center - x[0]) * (XSpeed.value / 10.0)),LinerSpeed.value * 0.5 * (YSpeedRate.value / 100.0),aSpeed)
        return list(Target_Speed)
    else:
        # print(target_angular)
        # print(center_point)
        # print(target_angular)
        # 这块要对偏转角度进行调参处理
        if target_angular >= AngleChangeLimit:
            aSpeed = (a+b)*(AngularSpeed.value / 10000.0)*target_angular*(AngleRate.value / 100.0)
        else:
            aSpeed = (a+b)*(AngularSpeed.value / 10000.0)*target_angular
        #得出目标速度
        #print(f"中心{x[0]}")
        Target_Speed = mecanumRun(((car_center - x[0]) * (XSpeed.value / 10.0)),LinerSpeed.value * 0.5, aSpeed)
        return list(Target_Speed)

def line_run(q, CarStatus , LinerSpeed_p, AngularSpeed_p, XSpeed_p, YSpeed_Rate, Angle_Rate):
    global LinerSpeed, AngularSpeed, XSpeed, YSpeedRate, AngleRate
    motor_dev = motor()
    LinerSpeed = LinerSpeed_p
    AngularSpeed = AngularSpeed_p
    XSpeed = XSpeed_p
    YSpeedRate = YSpeed_Rate
    AngleRate = Angle_Rate
    while True:
        list_x, list_y = q.get()
        # 对列表做最初步的处理
        list_x_out = []
        list_y_out = []
        for x, y in zip(list_x, list_y):
            if x != -1:
                list_x_out.append(int(x))
                list_y_out.append(int(y))
        if len(list_x_out) > 1 and CarStatus.value == 1:
            speed_list = CarRun(list_x_out,list_y_out)
            # print(speed_list)
        elif CarStatus.value == -1:
            # speed_list = [10, 10, 10, 10]
            speed_list = [0, 0, 0, 0]
        else:
            continue
        motor_dev.run(speed_list)