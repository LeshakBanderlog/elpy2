from actions import *
import acp
import window


# main logic
def loop(name):

    kills = 0
    useless = 0

    if name == 'over':
        while True:

            time.sleep(0.1)
            target_hp = get_target_hp()

            if target_hp > 0:
                if target_hp == 100:
                    useless += 1
                    if get_self_hp() < 80:
                        use_vamp()
                        use_attack()
                    else:
                        use_main_nuke()
                        use_attack()
                else:
                    use_attack()
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
                    if get_self_hp() < 80:
                        use_vamp()
                        use_attack()
                    else:
                        use_main_nuke()
                        use_attack()
                else:
                    use_attack()
            else:
                turn()

            if useless > 30:
                useless = 0
                unstuck()


i = 4
while i > 0:
    print(str(i) + '...')
    time.sleep(1)
    i -= 1

loop(NAME)
