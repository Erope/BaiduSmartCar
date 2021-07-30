import cv2  
import time
import numpy as np
from .two import *
from .search import *
from config import car_center, frame_show

# np.set_printoptions(threshold=np.inf)
# print(cv2.__version__)

def cv(q, XSpeed):
    cap = cv2.VideoCapture(0)
    #cap.set(cv2.CAP_PROP_FOURCC, 1196444237)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print(cap.get(cv2.CAP_PROP_FPS))
    time.sleep(0.5)
    assert int(cap.get(cv2.CAP_PROP_FPS)) == 30
    time.sleep(0.5)
    last_center = 40
    last_left = 0
    last_right = 79
    img_count = 0
    shizi_shibie_flag = -5
    XSpeed_bak = -1
    # 识别到5帧后认为自身在十字道
    while(1):
        # get a frame
        ret, img = cap.read()
        if ret is False:
            continue
        # 缩放
        img_count += 1
        # print(img.shape)
        img_small = cv2.resize(img, (80, 45), cv2.INTER_LANCZOS4)
        # print(img_small.shape)
        # return
        # cv2.imwrite('test.png', img)
        HSVImage = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
        # h, s, v = cv2.split(HSVImage)
        res = get_two(HSVImage)
        now_center = last_center
        now_left = last_left
        now_right = last_right
        center_list = []
        center_count = 0
        left_count = 0
        right_count = 0
        # 计算
        for i in range(img_small.shape[0] - 1, -1, -1):
            center, left, right = search(res, now_center, now_left, now_right, i, shizi_shibie_flag)
            # center, left, right = search(res, now_center, now_left, now_right, i, -5)
            if i == img_small.shape[0] - 1:
                last_center = center
                last_left = left
                last_right = right
            if center != -1:
                now_center = center
                center_count += 1
            if left != -1:
                now_left = left
                left_count += 1
            if right != -1:
                now_right = right
                right_count += 1
            center_list.append(center)
            if img_count == frame_show:
                if left!=-1 and right!=-1:
                    for j in range(0, 16):
                        img[i * 16 + j, center * 16, 0] = 0
                        img[i * 16 + j, center * 16, 1] = 0
                        img[i * 16 + j, center * 16, 2] = 255
                if left!=-1:
                    for j in range(0, 16):
                        img[i * 16 + j, left * 16, 0] = 255
                        img[i * 16 + j, left * 16, 1] = 0
                        img[i * 16 + j, left * 16, 2] = 0
                if right!=-1:
                    for j in range(0, 16):
                        img[i * 16 + j, right * 16, 0] = 0
                        img[i * 16 + j, right * 16, 1] = 255
                        img[i * 16 + j, right * 16, 2] = 0

        if center_count < 3:
            last_center = int(img_small.shape[1] / 2)
            last_left = 0
            last_right = int(img_small.shape[1] - 1)
        if left_count < 3 and right_count > 15:
            center_list = np.arange(40, 71.5, 0.7)
        if right_count < 3 and left_count > 15:
            center_list = np.arange(40, 8.5, -0.7)
        
        if right_count <= 30 and left_count <= 30 and center_count >= ((left_count + right_count) / 4.5) and abs(right_count - left_count) <= 10 :
            shizi_shibie_flag = min(shizi_shibie_flag + 1, 30)
            last_center = int(img_small.shape[1] / 2)
            last_left = 0
            last_right = int(img_small.shape[1] - 1)
            if XSpeed_bak == -1:
                XSpeed_bak = int(XSpeed.value)
                # XSpeed.value = int(XSpeed.value / 2)
                # print(XSpeed_bak)
            # center_list = [car_center] * 45
            # 降低纠正
            for i in range(0, len(center_list)):
                if center_list[i] != -1:
                    center_list[i] = (center_list[i] - car_center) / 3.0 + car_center
            # print("十字路口")
        else:
            shizi_shibie_flag = max(shizi_shibie_flag - 20, -5)
            center_list = center_list[0:34]
            if shizi_shibie_flag == -5 and XSpeed_bak != -1:
                XSpeed.value = int(XSpeed_bak)
                XSpeed_bak = -1
            # 认为遇到十字路口
        
        # 整体裁剪
        # 放入十字弯中，十字弯不裁剪
        # print(f"flag:{shizi_shibie_flag}")
        # print(f"left:{left_count}")
        # print(f"right:{right_count}")
        # center_list.reverse()
        q.put((center_list, range(0, len(center_list))))
        # print(center)
        # print(res)
        t = np.where(res == 1, 255, 0).astype(np.uint8)
        if img_count == frame_show:
            cv2.imshow("capture", img)
            cv2.waitKey(1)
            img_count = 0