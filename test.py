from run import *


if __name__ == '__main__':

    a = Process(target=acp)
    w = Process(target=window)
    if acp_on:
        a.start()
    if mode != '':
        w.start()

    time.sleep(3)
    print('start')

    if acp_on:
        a.join()
    if mode != '':
        w.join()

    print('stop')
