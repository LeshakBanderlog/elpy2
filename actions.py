from functions import *
from pyautogui import press, keyUp, keyDown, moveTo
from autoit import mouse_click as click
import time


resting = False


def reset_camera():

    press('pgdn')
    time.sleep(0.2)
    press('pgdn')
    time.sleep(0.2)
    press('pgdn')


def unstuck():

    moveTo(GAME_WINDOW_POS[2] - 250, GAME_WINDOW_POS[3])
    click()
    time.sleep(1)
    reset_camera()


def turn():

    method = TURN
    if method == 'key':
        keyDown('right')
        time.sleep(1)
        keyUp('right')
    else:
        moveTo(GAME_WINDOW_POS[2] / 2 + 50, GAME_WINDOW_POS[3] / 2 + 150)
        click()
        time.sleep(0.5)
        press('end')


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

        moveTo(center, left[1] + 30, 0.3)
        if find_from_targeted():
                click()
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
        time.sleep(0.2)
        picks -= 1
    cancel_target()


def rest(kills):

    global resting
    if not resting and get_self_mp() < 20:
        print('Time to rest! ' + kills + ' mobs killed per mana pool.')
        resting = True
        press(KEY_SIT)
        past_hp = 100
        while get_self_mp() < 100:
            time.sleep(5)
            current_hp = get_self_hp()
            if past_hp < current_hp:
                press(KEY_NEXT_TARGET)
                resting = False
                break
            past_hp = current_hp
        if resting:
            press(KEY_SIT)


def buff(kills):

    if not get_buff():
        print('Time to buff! ' + kills + ' mobs killed per buff.')
        press(KEY_BUFF)
        time.sleep(BUFF_TIME)


# usability wrappers
def use_main_nuke():

    press(KEY_MAIN_SKILL)
    time.sleep(0.1)
    press(KEY_SHOTS)


def use_second_nuke():

    press(KEY_SECOND_SKILL)
    time.sleep(0.1)
    press(KEY_SHOTS)


def use_vamp():

    press(KEY_VAMP_SKILL)
    time.sleep(0.1)
    press(KEY_SHOTS)


def use_attack():

    press(KEY_ATTACK)


def use_next_target():

    press(KEY_NEXT_TARGET)
    time.sleep(0.2)
