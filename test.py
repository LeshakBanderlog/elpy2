from run import *
import os

def file_checker():

    num = 1
    while True:
        file = 'img/target_' + num + '.bmp'
        if os.path.exists(file):
            num += 1
        else:
            break
    return num
