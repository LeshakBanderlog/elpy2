from run import *
import os


# Target List Generator ^^

def get_file_numer():
    num = 1
    while True:
        file = 'img/target_' + str(num) + '.bmp'
        if os.path.exists(file):
            num += 1
        else:
            break
    return num


def add_target(number):

    pos = TARGET_NAME_POS
    img = get_screen(pos[0], pos[1], pos[2], pos[3])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    for line in range(len(gray)):
        for pix in range(len(gray[line])):
            if gray[line][pix] == 218:
                gray[line][pix] = 255
            elif gray[line][pix] == 217:
                gray[line][pix] = 255
            elif gray[line][pix] == 191:
                gray[line][pix] = 255
            elif gray[line][pix] == 76:
                gray[line][pix] = 255
            else: 
                gray[line][pix] = 0

    num = 'img/target_' + str(number) + '.bmp'
    cv2.imwrite(num, gray)


while True:
    action = input('Add target to list(target must be selected in game? y/n  ')
    if action == 'y':
        file = get_file_numer()
        add_target(file)
        print('Target #' + str(file) + ' added.')
    elif action == 'n':
        break
    else:
        print('Incorrect input!')

print('Exit')
