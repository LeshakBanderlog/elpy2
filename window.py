from actions import *
from multiprocessing import Process


win = WINDOW


def enable():

    if win == 'over':
        while win != 'none':
            ...


if __name__ == '__main__':
    if win != 'none':
        win_prc = Process(target=enable)
        win_prc.start()