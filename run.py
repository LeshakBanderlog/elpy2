from pyautogui import keyDown, keyUp, moveTo, position, press
from PIL import ImageGrab, Image, ImageChops
from multiprocessing import Process, Event
from autoit import mouse_click as click
from settings import *
import numpy as np
import logging
import time
import cv2
import os


# VAR ------------------------------

mode = WINDOW
acp_on = ACP
resting = False
win_follow = False
targets = []
skills = []


# FUNCTIONS ------------------------

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
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
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

    def get_pixels(image, color):

        filled = 0
        pixels = image[0].tolist()
        for pixel in pixels:
            if pixel == color:
                filled += 1

        return filled

    pos = TARGET_BAR_POS
    img = get_screen(pos[0], pos[1], pos[2], pos[3])
    percent = -1

    if get_pixels(img, TARGET_BAR_COL) > 0:
        filled_pixels = get_pixels(img, TARGET_HP_COL)
        if filled_pixels == 0 and get_pixels(img, TARGET_EMPTY_HP_COL) == 0:
            percent = -1
        else:
            filled_pixels += 1
            percent = int(100 * filled_pixels / 150)

    return percent


def get_self_hp():
    # TODO: when hp is critical, it changes color(<30% = 0 for now)
    percent = get_bar(SELF_HP_COL, SELF_HP_POS)
    return percent


def get_self_mp():

    percent = get_bar(SELF_MP_COL, SELF_MP_POS)
    return percent


def get_win_hp():

    percent = get_bar(WIN_HP_COL, WIN_HP_POS)
    return percent


def get_win_mp():

    percent = get_bar(WIN_MP_COL, WIN_MP_POS)
    return percent


def get_buff():

    pos = BUFF_POS
    col = BUFF_COL
    filled_pixels = 0

    img = get_screen(pos[0], pos[1], pos[2], pos[3])

    pixels = img[0].tolist()
    for pixel in pixels:
        if pixel == col:
            filled_pixels += 1

    if filled_pixels > 0:
        return True
    return False


def get_list(file_name):

    num = 0
    img_list = []
    while True:
        file = 'img/' + file_name + '_' + str(num) + '.png'
        if os.path.exists(file):
            img_list.append(Image.open(file))
            num += 1
        else:
            break
    return img_list


def is_listed():

    img = ImageGrab.grab(bbox=(TARGET_NAME_POS[0],
                               TARGET_NAME_POS[1],
                               TARGET_NAME_POS[2],
                               TARGET_NAME_POS[3]))
    for victim in targets:
        img2 = victim
        dif = ImageChops.difference(img, img2)
        # noinspection PyTypeChecker
        pic = np.array(dif)
        gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        pixels = 0
        for line in range(len(gray)):
            for pix in range(len(gray[line])):
                if gray[line][pix] > 100:
                    pixels += 1
        if pixels == 0:
            return True
    return False


def is_ready(pos):

    if pos[0] == 'f':
        num = int(pos[1])
    else:
        num = int(pos)
    pos0 = SKILL_POS[0] + 37 * (int(num) - 1)
    pos1 = SKILL_POS[1]
    pos2 = SKILL_POS[2] + 37 * (int(num) - 1)
    pos3 = SKILL_POS[3]
    img = ImageGrab.grab(bbox=(pos0, pos1, pos2, pos3))

    for skill in skills:
        img2 = skill
        dif = ImageChops.difference(img, img2)
        # noinspection PyTypeChecker
        pic = np.array(dif)
        gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        pixels = 0
        for line in range(len(gray)):
            for pix in range(len(gray[line])):
                if gray[line][pix] > 100:
                    pixels += 1
        if pixels == 0:
            return True
    return False


# ACTIONS --------------------------

def reset_camera():

    press('pgdn')
    time.sleep(0.2)
    press('pgdn')
    time.sleep(0.2)
    press('pgdn')


def unstuck():

    logging.info('STUCK')
    cancel_target()
    moveTo(GAME_WINDOW_POS[2] - 250, GAME_WINDOW_POS[3])
    click()
    time.sleep(1)
    reset_camera()


def turn():

    method = TURN
    logging.info('TURN')
    if method == 'key':
        keyDown('right')
        time.sleep(1)
        keyUp('right')
    else:
        moveTo(GAME_WINDOW_POS[2] / 2 - 50, GAME_WINDOW_POS[3] / 2 + 170)
        click()
        time.sleep(0.5)
        press('end')
        time.sleep(0.7)


def set_target():

    logging.info('SEARCHING TARGET ->')
    pos = GAME_WINDOW_POS
    img = get_screen(pos[0], pos[1], pos[2], pos[3])

    cnts = get_target_centers(img)
    approxes = []
    hulls = []
    for cnt in cnts:
        approxes.append(cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True))
        hulls.append(cv2.convexHull(cnt))
        left = list(cnt[cnt[:, :, 0].argmin()][0])
        right = list(cnt[cnt[:, :, 0].argmax()][0])
        if right[0] - left[0] < 20:
            continue
        center = round((right[0] + left[0]) / 2)
        center = int(center)

        moveTo(center, left[1] + 30, 0.2)
        if find_from_targeted():
                click()
                time.sleep(0.5)
                if TARGET_LIST:
                    if is_listed() and get_target_hp() > 0:
                        logging.info('TARGET SET')
                        return True
                    else:
                        press('esc')
                elif get_target_hp() > 0:
                    logging.info('TARGET SET')
                    return True

    return False


def find_from_targeted():

    pos = GAME_WINDOW_POS
    template = cv2.imread('img/template_target.png', 0)
    roi = get_screen(pos[0], pos[1], pos[2], pos[3])
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    ret, th1 = cv2.threshold(roi, 224, 255, cv2.THRESH_TOZERO_INV)
    ret, th2 = cv2.threshold(th1, 135, 255, cv2.THRESH_BINARY)
    ret, tp1 = cv2.threshold(template, 224, 255, cv2.THRESH_TOZERO_INV)
    ret, tp2 = cv2.threshold(tp1, 135, 255, cv2.THRESH_BINARY)
    if not hasattr(th2, 'shape'):
        return False
    wth, hth = th2.shape
    wtp, htp = tp2.shape
    if wth > wtp and hth > htp:
        res = cv2.matchTemplate(th2, tp2, cv2.TM_CCORR_NORMED)
        if res.any():
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.7:
                return True
            else:
                return False
    return False


def cancel_target():

    press('esc')


def loot():

    picks = PICKS
    logging.info('LOOTING')
    while picks > 0:
        press(KEY_PICK)
        time.sleep(0.2)
        picks -= 1
    cancel_target()


def rest(kills):

    global resting
    if not resting and get_self_mp() < 20:
        logging.info('REST -> ' + str(kills) + ' mobs killed.')
        resting = True
        press(KEY_SIT)
        past_hp = 0
        while get_self_mp() < 100:
            time.sleep(5)
            current_hp = get_self_hp()
            if past_hp > current_hp:
                press(KEY_NEXT_TARGET)
                resting = False
                break
            past_hp = current_hp
        if resting:
            press(KEY_SIT)


def buff(kills):

    time.sleep(1)
    if not get_buff():
        logging.info('BUFF -> ' + str(kills) + ' mobs killed.')
        press(KEY_BUFF)
        time.sleep(BUFF_TIME)


# USABILITY WRAPPERS ---------------

def use_main_nuke():

    if is_ready(KEY_MAIN_SKILL):
        logging.info('USE: NUKE')
        press(KEY_MAIN_SKILL)
        time.sleep(0.2)
        press(KEY_SHOTS)


def use_second_nuke():

    if is_ready(KEY_SECOND_SKILL):
        logging.info('USE: SECOND NUKE')
        press(KEY_SECOND_SKILL)
        time.sleep(0.2)
        press(KEY_SHOTS)


def use_vamp():

    if is_ready(KEY_VAMP_SKILL):
        logging.info('USE: VAMP')
        press(KEY_VAMP_SKILL)
        time.sleep(0.2)
        press(KEY_SHOTS)


def use_heal():

    if is_ready(KEY_HEAL):
        logging.info('USE: HEAL')
        press(KEY_HEAL)
        time.sleep(0.2)
        press(KEY_SHOTS)


def use_attack():

    press(KEY_ATTACK)


def use_assist():

    press(KEY_ASSIST)
    time.sleep(0.5)


def use_next_target():

    press(KEY_NEXT_TARGET)
    time.sleep(0.2)


def use_follow():

    press(KEY_FOLLOW)
    time.sleep(0.5)


def use_win_attack():
    press(WIN_KEY_ATTACK)


def use_win_nuke():
    time.sleep(0.2)
    press(WIN_KEY_MAIN_SKILL)
    time.sleep(1)


def use_win_vamp():
    time.sleep(0.2)
    press(WIN_KEY_VAMP_SKILL)
    time.sleep(4)


def use_win_second_nuke():
    press(WIN_KEY_SECOND_SKILL)
    time.sleep(0.1)
    press(WIN_KEY_SHOTS)


def use_win_assist():
    global win_follow
    win_follow = False
    logging.debug('WIN assist')
    press(WIN_KEY_ASSIST)
    time.sleep(0.2)


def use_win_follow():
    global win_follow
    if not win_follow:
        time.sleep(0.2)
        logging.debug('WIN follow')
        press(WIN_KEY_FOLLOW)
        win_follow = True


def use_win_sit():
    time.sleep(0.2)
    press(WIN_KEY_SIT)
    time.sleep(0.2)


def use_win_pots():
    press(WIN_KEY_POTS)


# ADDS -----------------------------

def window(flag):

    logging.info('WINDOW ------- ON')
    use_win_follow()
    while not flag.is_set():

        time.sleep(0.2)

        target_hp = get_target_hp()
        if target_hp > 0:
            if target_hp < 100:
                use_win_assist()
                if get_win_hp() < 80:
                    use_win_vamp()
                use_win_nuke()
        elif target_hp == 0:
            use_win_follow()
        else:
            use_win_follow()

        if get_win_hp() < 40:
            use_win_pots()


def acp(flag):

    logging.info('ACP ---------- ON')
    hp = 100
    down = 0
    while not flag.is_set():
        if hp < 40:
            logging.info('ACP: HP < 40%')
            press(KEY_POTS)
            time.sleep(10)
        time.sleep(0.5)
        hp = get_self_hp()
        if hp < 0:
            while hp < 0:
                time.sleep(1)
                down += 1
                if down > IDLE:
                    logging.info('ZERO HP ' + str(IDLE) + 'SECONDS -> SHUTDOWN SYSTEM')
                    os.system('shutdown -s -t 60')


# MAIN LOGIC

def stand_alone_mode():

    kills = 0
    useless = 0
    logging.info('--- STAND ALONE MODE ---')

    while position()[0] < STOP[0] and position()[1] < STOP[1]:

        time.sleep(0.2)
        target_hp = get_target_hp()

        if target_hp > 0:
            if target_hp == 100:
                useless += 1
                if get_self_hp() < 80 and get_self_mp() > 15:
                    use_vamp()
                    use_attack()
                else:
                    use_attack()
            elif target_hp > 30:
                if get_self_hp() < 60 and get_self_mp() > 15:
                    use_vamp()
                else:
                    use_attack()
            else:
                use_attack()
        elif target_hp == 0:
            kills += 1
            use_next_target()
            useless = 0
            if get_target_hp() == 0:
                logging.info('TARGET ELIMINATED')
                loot()
                rest(kills)
                buff(kills)
                if get_win_hp() < 50:
                    logging.info('HEAL')
                    use_heal()
                    time.sleep(7)
            else:
                logging.info('NEXT TARGET ->')
        elif set_target():
            useless = 0
        else:
            turn()

        if useless > 100:
            useless = 0
            unstuck()

    logging.info('FINISHING -> HP ' + str(get_self_hp()) + '%. ' + str(kills) + ' mobs killed this session.')


def assist_mode():

    kills = 0
    logging.info('assist mode')

    while position()[0] < STOP[0] and position()[1] < STOP[1] or get_self_hp() == 0:

        time.sleep(0.1)
        target_hp = get_target_hp()

        if target_hp > 0:
            if get_self_hp() < 80 and get_self_mp() > 20:
                use_vamp()
            use_attack()
        elif target_hp == 0:
            kills += 1
            loot()
            use_follow()
            logging.info('%s mobs killed.', kills)
        else:
            use_assist()


# logging.basicConfig(filename='log.txt', format='%(asctime)s %(levelname)s:  %(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(levelname)s:  %(message)s', level=logging.INFO)

if __name__ == '__main__':

    targets = get_list(TARGET_FILE)
    skills = get_list(SKILL_FILE)
    e = Event()
    a = Process(target=acp, args=(e,))
    w = Process(target=window, args=(e,))

    if acp_on:
        a.start()
    if mode != '':
        w.start()

    time.sleep(3)
    logging.info('MAIN LOGIC --- ON')

    if ASSIST:
        assist_mode()
    else:
        stand_alone_mode()

    e.set()
    if acp_on:
        a.join()
        logging.info('ACP ---------- OFF')
    if mode != '':
        w.join()
        logging.info('WINDOW ------- OFF')

    logging.info('MAIN LOGIC --- OFF')
