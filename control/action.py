import time, serial

port = '/dev/ttyS0' # 舵机
sp = serial.Serial(port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
             xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=0, dsrdtr=False)

# 共四块舵机
# M1 抓取物块 
# M2 下降
# 上面两个负责将爪子放下去，抓物块，再加紧，再收回去
# M0 倒球 
# M3 举旗子

# 通过下面的这一串数据，依次发送，将舵机转动速度定为90°/s
Servo_speed0 = 'FF 01 00 14 00'  # 小球这里角速度变化要快，所以180度/s
Servo_speed1 = 'FF 01 01 0a 00' 
Servo_speed2 = 'FF 01 02 0a 00' 
Servo_speed3 = 'FF 01 03 0a 00' 
# 通过下面一串数据值，将对应的舵机放置到对应位置
# 举旗的部分，首先将旗子归位初始180度角，然后60度角度，120度角，0度角，三个角度
Servo_Flag_Init = 'FF 02 03 C4 09'  # 这个代表motor_3 给定角度180度，也就是归0状态
Servo_Flag_1 = 'FF 02 03 29 07'     # 这个代表motor_3 给定角度120度，也就是第一个旗子起来的样子
Servo_Flag_2 = 'FF 02 03 8F 04'     # 这个代表motor_3 给定角度60度，也就是第二个旗子举起来的样子
Servo_Flag_3 = 'FF 02 03 F4 01'     # 这个代表motor_3 给定角度0度， 也就是第三个旗子举起来的样子
# 抓取物块下降杆子状态
Servo_Down_Init = 'FF 02 02 56 05'  #  这个代表motor_2 给定角度为78度，为收起与初始时杆子状态
Servo_Down_Set  = 'FF 02 02 41 03'  #  这个代表motor_2 给定角度为30度，为杆子放下去状态
# 抓取物块爪子状态
Servo_Catch_Init = 'FF 02 01 15 02' # 这个代表motor_1 给定的角度为3度，为爪子初始张大状态
Servo_Catch_Set  = 'FF 02 01 35 04' # 这个代表motor_1 给定角度为52度，表示需要稳定抓取的状态
# 倾倒小球状态  M0
Servo_Ball_Init = 'FF 02 00 E7 04' # 这个是带着球走包括收回的状态，代表位置角度为68
Servo_Ball_Set  = 'FF 02 00 35 06' # 这个是代表迅速放下的角度，代表位置为98

# 配置串口基本参数并建立通信  这里不知道时com几，但是唯一确定貌似串口哪里只能传波特率9600的，快了概率会挂，好在完全够用，初始化调试
# ser = serial.Serial("COM1", 9600, 8, "E", timeout=50,stopbits=1) 

# # 串口发送数据,暂时未实现，将对应的传输进去后输出即可
def Send_Command(str):
    # 将格式串转换为正常格式串输出
    d = bytes.fromhex(str)
    sp.reset_output_buffer()
    sp.write(d)
    sp.flush()
    
# 将四个点击变化速度进行设置修改
def Set_Speed_Init():
    Send_Command(Servo_speed0)
    Send_Command(Servo_speed1)
    Send_Command(Servo_speed2)
    Send_Command(Servo_speed3)

# 举旗子 0 初始化 1 旗子1 2 旗子2 3旗子3
def Set_Flag(x):
    if x == 0:
        Send_Command(Servo_Flag_Init)
    elif x == 1:
        # 举旗子前先归原位
        Send_Command(Servo_Flag_Init)
        time.sleep(1)
        Send_Command(Servo_Flag_1)
    elif x == 2:
        # 举旗子前先归原位
        Send_Command(Servo_Flag_Init)
        time.sleep(1)
        Send_Command(Servo_Flag_2)
    elif x == 3:
        # 举旗子前先归原位
        Send_Command(Servo_Flag_Init)
        time.sleep(1)
        Send_Command(Servo_Flag_3)

# 下降杆子的控制 0 初始状态  1 下降抓取状态
def Set_Down(x):
    # 初始状态
    if x == 0:
        Send_Command(Servo_Down_Init)
    elif x == 1:
        Send_Command(Servo_Down_Set) # 下降到位

# 抓取方块 0 回归初始状态 1 抓取
def Set_Catch(x):
    if x == 0:
        Send_Command(Servo_Catch_Init)
    elif x == 1:
        Send_Command(Servo_Catch_Set)
        
# 倾倒小球的动作 0 是出发时的状态 1 是完成小球动作
def Set_Dump_Ball(x):
    if x == 0: # 出发的初始状态
        Send_Command(Servo_Ball_Init)
    # 这个代表倾倒动作，根据手动测试，倒下去后迅速再抬起来，可以较好的完成任务。
    # 目前倾倒和抬起延时800ms,可更改，不能低于500，防止无法完成角度转弯
    elif x == 1:  
        Send_Command(Servo_Ball_Set)
        time.sleep(1)
        Send_Command(Servo_Ball_Init)


