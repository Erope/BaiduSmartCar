KEY_List = [26, 19, 24, 23, 4]
# 上 下 左 右 中
# 上去掉 7
BUTTON_List = [16, 20, 12, 21]
# 按钮对应城池
Key_City = ["定襄郡", "代郡", "敦煌"]
menu_main = ["下 - 旗帜选择", "左 - 速度修改", "右 - 特殊运行"]
menu_flag = ["旗帜选择", "按下对应按钮"]
menu_speed = ["速度修改"]
menu_special_run = ["特殊运行"]
Status = {
    -1: "停止复位",
    0: "主控开始",
    1: "巡线状态",
    2: "底部校准",
    3: "执行任务",
    4: "特殊执行"
}

# 速度步进
speed_step = 1