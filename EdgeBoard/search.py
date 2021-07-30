import numpy as np
def search(img, searchh):
    lflag = 0
    for i in range(int(img.shape[1] / 2 - 5), int(img.shape[1] / 2 + 5)):
        if img[searchh, i] == 1:
            lflag += 1
    # max
    return lflag