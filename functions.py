from PIL import ImageGrab
from settings import *
import numpy as np
import cv2


def get_screen(x1, y1, x2, y2):
    screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    img = np.array(screen.getdata(), dtype=np.uint8).reshape((screen.size[1], screen.size[0], 3))
    return img


def get_target_centers(img):

    # Hide your name in first camera position (default)
    img[295:315, 467:557] = (0, 0, 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('1_gray_img.png', gray)

    # Find only white text
    ret, threshold1 = cv2.threshold(gray, 252, 255, cv2.THRESH_BINARY)
    # cv2.imwrite('2_threshold1_img.png', threshold1)

    # Morphological transformation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 5))
    closed = cv2.morphologyEx(threshold1, cv2.MORPH_CLOSE, kernel)
    # cv2.imwrite('3_morphologyEx_img.png', closed)
    closed = cv2.erode(closed, kernel, iterations=1)
    # cv2.imwrite('4_erode_img.png', closed)
    closed = cv2.dilate(closed, kernel, iterations=1)
    # cv2.imwrite('5_dilate_img.png', closed)

    (_, centers, hierarchy) = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return centers


def get_bar(col, pos):

    filled_pixels = 1

    img = get_screen(pos[0], pos[1], pos[2], pos[3])

    pixels = img[0].tolist()
    for pixel in pixels:
        if pixel == col:
            filled_pixels += 1

    percent = int(100 * filled_pixels / 150)
    return percent


def get_target_hp():

    percent = get_bar(TARGET_HP_COL, TARGET_HP_POS)
    return percent


def get_self_hp():

    percent = get_bar(SELF_HP_COL, SELF_HP_POS)
    return percent


def get_self_mp():

    percent = get_bar(SELF_MP_COL, SELF_MP_POS)
    return percent


def get_buff():

    pos = BUFF_POS
    col = BUFF_COL
    filled_pixels = 1

    img = get_screen(pos[0], pos[1], pos[2], pos[3])

    pixels = img[0].tolist()
    for pixel in pixels:
        if pixel == col:
            filled_pixels += 1

    if filled_pixels > 0:
        return True
    return False
