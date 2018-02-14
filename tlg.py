from run import *


# Target List Generator ^^

def get_file_number():
    num = 1
    while True:
        file = 'img/target_' + str(num) + '.png'
        if os.path.exists(file):
            num += 1
        else:
            break
    return num


def add_target(number):

    pos = TARGET_NAME_POS
    img = ImageGrab.grab(bbox=(pos[0], pos[1], pos[2], pos[3]))
    num = 'img/target_' + str(number) + '.png'
    img.save(num)


while True:
    action = input('Add target to list?(target must be selected in game) y/n  ')
    if action == 'y':
        file_num = get_file_number()
        add_target(file_num)
        print('Target #' + str(file_num) + ' added.')
    elif action == 'n':
        break
    else:
        print('Incorrect input!')

print('Exit')
