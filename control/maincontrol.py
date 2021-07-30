import time, serial 
from motor.i2c import motor
from motor.main import mecanumRun
import re
from .action import Set_Flag, Set_Catch, Set_Down, Set_Dump_Ball
from config import Skip_Calibrate
import requests
from requests.adapters import HTTPAdapter

CarStatus = None
CityList = None
FlagRun = None
TaskStatus = 0
CityId = 0
motor_dev = motor()
bps = 115200
sp = None
sp_shoot = None

# sp.open()
last_sp_time = 2000000000
time_limit = 2
Special_Run = False

def ControlStart():
    # 主控开始状态， 0
    # 在初始阶段触发，用于提前向前走一点点
    motor_dev.run([10, 10, 10, 10])
    time.sleep(0.7)

def LineControl():
    # 巡线状态，1
    # 是大部分情况下的状态，用于道路巡线，将控制器交给巡线程序
    # 这部分处理外部设备状态，即底部OpenMV设备
    # print("进入巡线")
    global last_sp_time, CarStatus
    data = sp.read_all()
    if len(data) != 0 and (time.time() - last_sp_time) >= time_limit:
        # 如果底部有数据则进入校准状态
        CarStatus.value = 2
        sp.reset_input_buffer()
        # 停止接收数据
        last_sp_time = 2000000000
        return True
    else:
        return False

def EdgeBoardControl():
    # EdgeBoard的摄像头读取控制，也就是侧方位摄像头
    # 用于在部分任务区域进行较为精准的停车
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=0))
    start_count = 0
    print("正在进行侧方位EdgeBoard校准...")
    while True:
        try:
            r = s.get('http://192.168.137.254:5000/get_num', timeout=1)
            # print(r.status_code)
            # print(requests.codes.ok)
            assert r.status_code == requests.codes.ok
            start_count += 1
            if start_count >= 120:
                print("出错，侧方位EdgeBoard超时!")
            elif start_count >= 20 and r.text == '-1':
                print("侧方位EdgeBoard没有检测到边线！")
                return
            elif start_count < 20:
                continue
            if r.text != '-1':
                if int(r.text) < 5:
                    print(str(time.time) + " 可能出线！!")
                if int(r.text) < 16:
                    print("即将压线！!")
                    motor_dev.run(mecanumRun(2, 0, 0))
                    time.sleep(0.05)
                    motor_dev.run([0, 0, 0, 0])
                    time.sleep(0.5)
                    start_count += 30
                elif int(r.text) > 40:
                    print("距边线较远！！")
                    motor_dev.run(mecanumRun(-2, 0, 0))
                    time.sleep(0.05)
                    motor_dev.run([0, 0, 0, 0])
                    time.sleep(0.5)
                    start_count += 30
                else:
                    print("侧方位EdgeBoard校准成功！")
                    return
        except BaseException as e:
            print(f"出错，侧方位EdgeBoard校准失败!错误信息: {str(e)}")
            return

def CalibrateControl():
    # 底部色块校准状态，2
    # 由OpenMV触发，从巡线状态转换而来
    # 主要将车辆调节至中点位置
    print("进入底部色块校准")
    global TaskStatus, CarStatus
    sp.reset_input_buffer()
    time.sleep(0.001)
    start_time = time.time()
    fail_time = 0
    while True:
        if CarStatus.value != 2:
            print("状态变化，退出色块校准")
            return
        if time.time() - start_time > 6:
            print("校准超时...强行执行任务")
            CarStatus.value = 3 # 执行任务
            motor_dev.run([0, 0, 0, 0])
            time.sleep(0.001)
            motor_dev.run([0, 0, 0, 0])
            return
        data = sp.read_all().decode()
        if len(data) == 0:
            # print("暂未接收到坐标数据...")
            # motor_dev.run([0, 0, 0, 0])
            if fail_time >= 80:
                motor_dev.run([0, 0, 0, 0])
            else:
                fail_time += 1
            time.sleep(0.001)
            continue
        elif len(data) > 10:
            # [120,320]
            # print(str(data))
            print("可能有积压数据...清空缓冲区...")
            sp.reset_input_buffer()
            motor_dev.run([0, 0, 0, 0])
            time.sleep(0.001)
            continue
        elif len(data) < 6:
            print(data)
            print("无效数据1...清空缓冲区...")
            sp.reset_input_buffer()
            motor_dev.run([0, 0, 0, 0])
            continue
        # 数据正常
        pattern = re.compile(r"\[(\d+),(\d+)]")
        match = pattern.match(data)
        if match and len(match.groups()) == 2:
            print(match.groups())
            now_y = int(match.groups()[1])
            speed_x = 0
            speed_y = 0
            # if now_x < 50:
            #   speed_x = 3
            # elif now_x > 58:
            #    speed_x = -3
            if now_y < 40:
                speed_y = 2
            elif now_y < 66:
                speed_y = 1
            elif now_y > 90:
                speed_y = -2
            elif now_y > 78:
                speed_y = -1
            if speed_x == 0 and speed_y == 0:
                print("已校准")
                CarStatus.value = 3 # 执行任务
                motor_dev.run([0, 0, 0, 0])
                time.sleep(0.001)
                motor_dev.run([0, 0, 0, 0])
                return
            fail_time = 0
            motor_dev.run(mecanumRun(speed_x, speed_y, 0))
            time.sleep(0.005)
        else:
            print("无效数据2...清空缓冲区...")
            sp.reset_input_buffer()
            motor_dev.run([0, 0, 0, 0])
        time.sleep(0.001)

def CityTask(city_id):
    # 模拟举旗
    Set_Flag(CityList[city_id] + 1)
    time.sleep(2.5)
    sp_shoot.write('G'.encode())
    sp_shoot.flush()
    time.sleep(6)
    time.sleep(0.5)
    Set_Flag(0)
    time.sleep(1.5)

def ShootSend():
    sp_shoot.reset_output_buffer()
    sp_shoot.write('X'.encode())
    sp_shoot.flush()
    time.sleep(5)
    motor_dev.run(mecanumRun(1, 0, 0))
    time.sleep(0.01)
    for _ in range(0, 10):
        motor_dev.run([0, 0, 0, 0])
        time.sleep(0.002)

def ShootTask():
    # 打靶任务
    # 和OpenMV进行校准
    print("进入靶子校准")
    global TaskStatus, CarStatus
    sp_shoot.reset_input_buffer()
    motor_dev.run(mecanumRun(-3, 0, 0))
    time.sleep(0.2)
    for _ in range(0, 10):
        motor_dev.run([0, 0, 0, 0])
        time.sleep(0.002)
    start_time = time.time()
    count_zhun = 0
    # EdgeBoardControl()
    while True:
        if CarStatus.value != 3:
            print("状态变化，退出靶子校准")
            return
        if time.time() - start_time > 6:
            print("校准超时...强行发送打靶指令...")
            motor_dev.run([0, 0, 0, 0])
            time.sleep(0.05)
            motor_dev.run([0, 0, 0, 0])
            time.sleep(0.01)
            ShootSend()
            return
        data = sp_shoot.read_all().decode()
        if len(data) == 0:
            # print("暂未接收到坐标数据...")
            # motor_dev.run([0, 0, 0, 0])
            time.sleep(0.001)
            continue
        elif len(data) > 5:
            # [120]
            print(f"数据: {data} 长度: {len(data)}")
            print("靶子校准可能有积压数据...清空缓冲区...")
            sp.reset_input_buffer()
            motor_dev.run([0, 0, 0, 0])
            time.sleep(0.001)
            continue
        elif len(data) < 3:
            print(data)
            print("无效数据1...清空缓冲区...")
            sp.reset_input_buffer()
            motor_dev.run([0, 0, 0, 0])
            continue
        # 数据正常
        pattern = re.compile(r"\[(\d+)\]")
        match = pattern.match(data)
        if match and len(match.groups()) == 1:
            print(match.groups())
            now_y = int(match.groups()[0])
            speed_x = 0
            speed_y = 0
            # if now_x < 50:
            #   speed_x = 3
            # elif now_x > 58:
            #    speed_x = -3
            if now_y < 87:
                speed_y = -1
            elif now_y > 93:
                speed_y = 1
            if speed_x == 0 and speed_y == 0:
                count_zhun += 1
                if count_zhun <= 3:
                    continue
                print("靶心已校准")
                motor_dev.run([0, 0, 0, 0])
                time.sleep(0.05)
                motor_dev.run([0, 0, 0, 0])
                time.sleep(0.01)
                ShootSend()
                return
            motor_dev.run(mecanumRun(speed_x, speed_y, 0))
            time.sleep(0.001)
        else:
            print("无效数据2...清空缓冲区...")
            sp.reset_input_buffer()
            motor_dev.run([0, 0, 0, 0])
        time.sleep(0.001)


def TaskControl():
    # 任务执行函数，3
    global CityId
    # 停止电机
    for _ in range(0, 10):
        motor_dev.run([0, 0, 0, 0])
        time.sleep(0.002)
    if Special_Run and TaskStatus != 10:
        if TaskStatus != 3 and TaskStatus != 4 and TaskStatus != 5:
            CarStatus.value = 1
            return
        if FlagRun[TaskStatus - 3] == 0:
            CarStatus.value = 1
            return
    if TaskStatus == 1 or TaskStatus == 2 or TaskStatus == 9:
        # 城池任务
        CityTask(CityId)
        CityId += 1
    elif TaskStatus == 3 or TaskStatus == 4 or TaskStatus == 5:
        # 打靶任务
        ShootTask()
    elif TaskStatus == 6:
        # 宿营任务
        time.sleep(1)
        EdgeBoardControl()
        time.sleep(1)
        # 左移
        motor_dev.run(mecanumRun(7, 0, 0))
        time.sleep(3.0)
        motor_dev.run([0 ,0 ,0 ,0])
        time.sleep(5)
        # 亮灯
        sp_shoot.write('R'.encode())
        sp_shoot.flush()
        time.sleep(4.5)
        # 右移
        motor_dev.run(mecanumRun(-7, 0, 0))
        time.sleep(3.0)
        motor_dev.run([0 ,0 ,0 ,0])
        time.sleep(1)
    elif TaskStatus == 7:
        # 拿战利品
        EdgeBoardControl()
        for i in range(0, 5):
            motor_dev.run([0 ,0 ,0 ,0])
        time.sleep(1)
        
        # motor_dev.run(mecanumRun(-3, 0, 0))
        # time.sleep(0.1)

        # 归位
        #Set_Catch(0)
        #Set_Down(0)
        #time.sleep(1)
        # 先下降
        Set_Down(1)
        time.sleep(0.7)
        # 抓取
        Set_Catch(1)
        time.sleep(0.7)
        # Set_Catch(0)
        # time.sleep(5)
        # 收回
        Set_Down(0)
        time.sleep(0.6)
        motor_dev.run(mecanumRun(3, 0, 0))
        time.sleep(0.3)
        motor_dev.run([0 ,0 ,0 ,0])
        time.sleep(0.4)
    elif TaskStatus == 8:
        # 放粮草
        EdgeBoardControl()
        time.sleep(1)
        motor_dev.run(mecanumRun(-3, 0, 0))
        time.sleep(0.7)
        motor_dev.run([0 ,0 ,0 ,0])
        # 归位
        Set_Dump_Ball(0)
        time.sleep(1)
        Set_Dump_Ball(1)
        time.sleep(0.4)

        motor_dev.run(mecanumRun(3, 0, 0))
        time.sleep(0.8)
        motor_dev.run([0 ,0 ,0 ,0])
        time.sleep(0.4)
    elif TaskStatus == 10:
        motor_dev.run([3 ,3 ,3 ,3])
        time.sleep(0.05)
        motor_dev.run([0 ,0 ,0 ,0])
        time.sleep(0.01)
    else:
        print("错误的任务状态！！！")
    if TaskStatus == 10:
        CarStatus.value = -1
    else:
        CarStatus.value = 1

def CarControl():
    # 循环判断是否发车
    global CarStatus, last_sp_time, TaskStatus, CityId, Special_Run
    while True:
        if CarStatus.value == -1:
            # 停车，重置状态
            sp.reset_input_buffer()
            last_sp_time = 2000000000
            TaskStatus = 0
            CityId = 0
        if CarStatus.value == 0:
            Special_Run = False
            ControlStart()
            last_sp_time = time.time() + 0.4
            CarStatus.value = 1
            sp.reset_input_buffer()
        elif CarStatus.value == 1:
            # 巡线状态
            if LineControl():
                # 跳过延时，直接进入校准状态
                continue
        elif CarStatus.value == 2:
            # 底部校准
            if Skip_Calibrate[TaskStatus] == 1:
                if not Special_Run:
                    CalibrateControl()
                elif TaskStatus >= 2 and TaskStatus <= 4 and FlagRun[TaskStatus - 3]:
                    CalibrateControl()
                else:
                    CarStatus.value = 3 # 执行任务
                    motor_dev.run([0, 0, 0, 0])
                    time.sleep(0.001)
            else:
                CarStatus.value = 3 # 执行任务
                motor_dev.run([0, 0, 0, 0])
                time.sleep(0.001)
            TaskStatus += 1
        elif CarStatus.value == 3:
            # 执行任务
            # print("执行任务")
            motor_dev.run([0, 0, 0, 0])
            time.sleep(0.001)
            TaskControl()
            last_sp_time = time.time()
        elif CarStatus.value == 4:
            Special_Run = True
            ControlStart()
            last_sp_time = time.time() + 0.5
            CarStatus.value = 1
            sp.reset_input_buffer()
        time.sleep(0.001)

def CarControlRun(Car_Status, City_List, Flag_Run):
    global CarStatus, CityList, sp, sp_shoot, FlagRun
    CarStatus = Car_Status
    CityList = City_List
    FlagRun = Flag_Run
    port = '/dev/mv_1'
    port_shoot = '/dev/mv_0'
    sp = serial.Serial(port, baudrate=bps, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=0, dsrdtr=True)
    sp.setDTR(True) # dsrdtr is ignored on Windows.

    sp_shoot = serial.Serial(port_shoot, baudrate=bps, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=0, dsrdtr=True)
    sp_shoot.setDTR(True) # dsrdtr is ignored on Windows.
    CarControl()