import numpy as np
import cv2
from config import limit
def get_two(img, img_bgr):
    rgbarr = cv2.split(img)
    rgbtrure = cv2.split(img_bgr)
    res = np.ones((img.shape[0], img.shape[1]), np.uint8)
    for i, j in zip(rgbarr, limit):
        res = res * (np.where(i >= j[0], 1, 0) * np.where(i <= j[1], 1, 0))
    res = res * (np.where(rgbtrure[2] >= 90, 1, 0))
    return res
