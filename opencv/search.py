import cv2
import numpy as np
def search(img, center, now_left, now_right, searchh, shizi_shibie_flag):
    h, w = img.shape
    if now_left == -1:
        now_left = 0
    if now_right == -1:
        now_right = int(w - 1)
    if center == -1:
        center = int(w / 2)
    lflag = 0
    allow_num = 8
    if shizi_shibie_flag > -5:
        allow_num = 1
    if shizi_shibie_flag >= 0:
        # print("缩减")
        left_limit = 8
        right_limit = w - 8
    else:
        left_limit = -1
        right_limit = w
    # searchh = 30
    search_list = [0] * w
    for i in range(center, -1, -1):
        if img[searchh, i] == 1:
            lflag += 1
        elif lflag > 0:
            lflag = max(lflag - 2, 0)
        search_list[i] = lflag
    lflag = 0
    for i in range(center, w):
        if img[searchh, i] == 1:
            lflag += 1
        elif lflag > 0:
            lflag = max(lflag - 2, 0)
        search_list[i] = lflag
    
    # max
    max_num = 0
    max_index = -1
    is_Found = False
    for i in range(max(center - 3, left_limit + 1), max(now_left - allow_num, left_limit), -1):
        if search_list[i] > max_num:
            max_num = search_list[i]
            max_index = i
        if max_num >= 3:
            is_Found = True
        if is_Found and search_list[i] == 0:
            break
    left = max_index
    # print(test_list)
    # print(search_list[0:40])
    # print(left)

    max_num = 0
    max_index = -1
    is_Found = False
    for i in range(min(center + 3, right_limit - 1), min(right_limit, now_right + allow_num)):
        if search_list[i] > max_num:
            max_num = search_list[i]
            max_index = i
        if max_num >= 3:
            is_Found = True
        if is_Found and search_list[i] == 0:
            break
    right = max_index

    if left == -1 or right == -1:
        return (-1, left, right)
    else:
        return (int((left + right) / 2), left, right)
    # return (int((left + right) / 2), left, right)

