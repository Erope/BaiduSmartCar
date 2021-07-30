import cv2
import numpy as np
from search import search
from two import get_two

class VideoCamera(object):
    def __init__(self):
        # 通过opencv获取实时视频流
        self.video = cv2.VideoCapture(2)
        self.video.set(cv2.CAP_PROP_FOURCC, 1196444237)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, img = self.video.read()
        if not success:
            return None
        img_small = cv2.resize(img, (80, 45), cv2.INTER_LANCZOS4)
        HSVImage = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
        res = get_two(HSVImage, img_small)
        is_Found = False
        for i in range(0, img_small.shape[0]):
            img_num = search(res, i)
            if img_num >= 7 and not is_Found:
                is_Found = True
                # print("Found!")
                for j in range(0, img_small.shape[1]):
                    for p in range(0, 16):
                        img[i * 16, j * 16 + p, 0] = 0
                        img[i * 16, j * 16 + p, 1] = 255
                        img[i * 16, j * 16 + p, 2] = 0
            for j in range(0, img_small.shape[1]):
                if res[i, j] == 1:
                    for p in range(0, 16):
                        img[i * 16 + p, j * 16, 0] = 0
                        img[i * 16 + p, j * 16, 1] = 0
                        img[i * 16 + p, j * 16, 2] = 255
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()
        
    def get_num(self):
        success, img = self.video.read()
        if not success:
            return -1
        img_small = cv2.resize(img, (80, 45), cv2.INTER_LANCZOS4)
        HSVImage = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
        res = get_two(HSVImage, img_small)
        is_Found = False
        for i in range(0, img_small.shape[0]):
            img_num = search(res, i)
            if img_num >= 7 and not is_Found:
                is_Found = True
                return i
        return -1

cap=VideoCamera()