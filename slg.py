from run import *


# Skill List Generator ^^

def add_skill(number):

    pos0 = SKILL_POS[0] + 37 * (int(number) - 1)
    pos1 = SKILL_POS[1]
    pos2 = SKILL_POS[2] + 37 * (int(number) - 1)
    pos3 = SKILL_POS[3]
    img = ImageGrab.grab(bbox=(pos0, pos1, pos2, pos3))
    num = 'img/skill_' + str((int(number) - 1)) + '.png'
    img.save(num)


while True:
    skill_num = input('Input action bar position of skill(1-12) or "n" if you want to quit: ')
    if skill_num == 'n':
        break
    else:
        add_skill(skill_num)
        print('Skill #' + str(skill_num) + ' added.')


print('Exit')
