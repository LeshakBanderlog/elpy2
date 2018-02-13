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


# noinspection PyTypeChecker
def is_target_in_list():

    pos = TARGET_NAME_POS
    img = ImageGrab.grab(bbox=(pos[0], pos[1], pos[2], pos[3]))
    ok = False
    num = 1

    while True:
        file = 'img/target_' + str(num) + '.png'
        if os.path.exists(file):
            img2 = Image.open(file)
            dif = ImageChops.difference(img, img2)
            pic = np.array(dif)
            gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
            pixels = 0
            for line in range(len(gray)):
                for pix in range(len(gray[line])):
                    if gray[line][pix] > 100:
                        pixels += 1
            if pixels == 0:
                ok = True
                break
            num += 1
        else:
            break

    return ok


# ACTIONS --------------------------

def reset_camera():

    press('pgdn')
    time.sleep(0.2)
    press('pgdn')
    time.sleep(0.2)
    press('pgdn')


def unstuck():

    cancel_target()
    moveTo(GAME_WINDOW_POS[2] - 250, GAME_WINDOW_POS[3])
    click()
    time.sleep(1)
    reset_camera()


def turn():

    method = TURN
    if method == 'key':
        keyDown('right')
        time.sleep(0.7)
        keyUp('right')
    else:
        moveTo(GAME_WINDOW_POS[2] / 2 - 50, GAME_WINDOW_POS[3] / 2 + 170)
        click()
        time.sleep(0.5)
        press('end')
        time.sleep(0.7)


def set_target():

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
                    if is_target_in_list() and get_target_hp() > 0:
                        return True
                    else:
                        press('esc')
                elif get_target_hp() > 0:
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
    while picks > 0:
        press(KEY_PICK)
        time.sleep(0.3)
        picks -= 1
    cancel_target()


def rest(kills):

    global resting
    if not resting and get_self_mp() < 20:
        logging.info('Time to rest! ' + str(kills) + ' mobs killed.')
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
        logging.info('Time to buff! ' + str(kills) + ' mobs killed.')
        press(KEY_BUFF)
        time.sleep(BUFF_TIME)
        cancel_target()


# USABILITY WRAPPERS ---------------

def use_main_nuke():

    press(KEY_MAIN_SKILL)
    time.sleep(0.2)
    press(KEY_SHOTS)


def use_second_nuke():

    press(KEY_SECOND_SKILL)
    time.sleep(0.2)
    press(KEY_SHOTS)


def use_vamp():

    press(KEY_VAMP_SKILL)
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
    time.sleep(4)


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
    logging.info('WIN assist')
    press(WIN_KEY_ASSIST)
    time.sleep(0.2)


def use_win_follow():
    global win_follow
    if not win_follow:
        time.sleep(0.2)
        logging.info('WIN follow')
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

    if mode == 'summoner':
        logging.info('WINDOW ------- ON')
        use_win_follow()
        while not flag.is_set():

            time.sleep(0.2)

            target_hp = get_target_hp()
            if target_hp > 0:
                if 100 > target_hp > 20:
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

        logging.info('WINDOW ------- OFF')

    elif mode == 'over':
        ...


def acp(flag):

    logging.info('ACP ---------- ON')
    while not flag.is_set():
            if get_self_hp() < 40:
                press(KEY_POTS)
            time.sleep(0.5)
    logging.info('ACP ---------- OFF')


# MAIN LOGIC

def stand_alone_mode(name):

    kills = 0
    useless = 0
    flame = False
    logging.info('stand_alone mode')

    if name == 'over':
        logging.info('enabled OVERLORD logic')
        while position()[0] < STOP[0] and position()[1] < STOP[1] or get_self_hp() == 0:

            time.sleep(0.1)
            target_hp = get_target_hp()

            if target_hp > 0:
                if target_hp == 100:
                    useless += 1
                    if get_self_hp() < 80:
                        use_vamp()
                        use_attack()
                    else:
                        if not flame:
                            use_main_nuke()
                            flame = True
                        use_attack()
                else:
                    use_attack()
            elif target_hp == 0:
                kills += 1
                use_next_target()
                useless = 0
                if get_target_hp() == 0:
                    loot()
                    rest(kills)
                    buff(kills)
                    if get_self_hp() < 50:
                        use_second_nuke()
                        time.sleep(7)
            elif set_target():
                useless = 0
                flame = False
                if target_hp == 100:
                    useless += 1
                    if get_self_hp() < 80:
                        use_vamp()
                        use_attack()
                    else:
                        if not flame:
                            use_main_nuke()
                            flame = True
                        use_attack()
                else:
                    use_attack()
            else:
                turn()

            if useless > 80:
                logging.info('Looks loki im stuck... Go somewhere.')
                useless = 0
                unstuck()

    if name == 'summoner':
        logging.info('enabled SUMMONER logic')
        while position()[0] < STOP[0] and position()[1] < STOP[1] or get_self_hp() == 0:

            time.sleep(0.1)
            target_hp = get_target_hp()

            if target_hp > 0:
                if target_hp == 100:
                    useless += 1
                if get_win_mp() < 10:
                    use_attack()
                elif target_hp < 33:
                    use_second_nuke()
                elif get_self_hp() < 80:
                    use_vamp()
                else:
                    use_main_nuke()
            elif target_hp == 0:
                kills += 1
                use_next_target()
                if get_target_hp() == 0:
                    loot()
                    rest(kills)
                    buff(kills)
            elif set_target():
                useless = 0
                if target_hp == 100:
                    useless += 1
                if get_win_mp() < 10:
                    use_attack()
                elif target_hp < 33:
                    use_second_nuke()
                elif get_self_hp() < 80:
                    use_vamp()
                else:
                    use_main_nuke()
            else:
                turn()

            if useless > 80:
                logging.info('Looks loki im stuck... Go somewhere.')
                useless = 0
                unstuck()


def assist_mode(name):

    kills = 0
    logging.info('assist mode')

    if name == 'over':
        logging.info('enabled OVERLORD logic')
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

    if name == 'summoner':
        ...


# START

logging.basicConfig(format='%(asctime)s %(levelname)s:  %(message)s', level=logging.INFO)

if __name__ == '__main__':

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
        assist_mode(NAME)
    else:
        stand_alone_mode(NAME)

    e.set()
    if acp_on:
        a.join()
    if mode != '':
        w.join()

    logging.info('MAIN LOGIC --- OFF')
