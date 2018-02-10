from actions import *
from multiprocessing import Process


acp_on = ACP


def enable():

    while acp_on:
        self_hp = get_self_hp()
        if self_hp < 40:
            press(KEY_POTS)
            time.sleep(POTS_CD)
        else:
            time.sleep(0.5)


if __name__ == '__main__':
    if acp_on:
        acp_prc = Process(target=enable)
        acp_prc.start()
