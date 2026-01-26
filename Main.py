import random
import time
import os
import logging
import sys
from lang import load, t

# cross-platform clear
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# choose language from --lang argument or LANG environment
lang_arg = None
if '--lang' in sys.argv:
    idx = sys.argv.index('--lang') + 1
    if idx < len(sys.argv):
        lang_arg = sys.argv[idx]
else:
    env = os.environ.get('LANG', '')
    if env:
        lang_arg = env[:2]

load(lang_arg or 'en')

# configure logging to log.txt with utf-8 encoding
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')
logging.info(t('game_start', time=time.strftime("%Y-%m-%d %H:%M:%S")))

witch_good = True
witch_bad = True

# helper to get int input with validation
def input_int(prompt, min_v=1, max_v=6, allow_empty=False, valid_set=None):
    while True:
        try:
            s = input(prompt)
            if allow_empty and s == '':
                return None
            v = int(s)
            if v < min_v or v > max_v:
                print(t('please_type_again'))
                continue
            if valid_set is not None and v not in valid_set:
                print(t('please_type_again'))
                continue
            return v
        except ValueError:
            print(t('please_type_again'))


def werewolf():
    global player, tonight_died
    if "Werewolf" in player:
        time.sleep(1)
        # ask the werewolves to choose a target (1-based)
        killed_player = input_int(t('who_kill'))
        logging.info(t('werewolf_killed', n=killed_player))
        clear_screen()
        tonight_died.append(killed_player)
        time.sleep(1)
        # if there are two alive werewolves, allow a second kill (keeps original behavior)
        if player.count("Werewolf") == 2:
            killed_player = input_int(t('who_kill'))
            logging.info(t('werewolf_killed', n=killed_player))
            clear_screen()
            if killed_player not in tonight_died:
                tonight_died.append(killed_player)
            time.sleep(1)


def witch():
    global player, witch_good, witch_bad
    if "Witch" in player:
        time.sleep(1)
        if not tonight_died:
            return
        with open('log.txt', 'a', encoding='utf-8'):
            # show who were chosen by werewolves
            if len(tonight_died) == 1:
                print(t('witch_notice_killed_single', n=tonight_died[0]))
            else:
                # join numbers
                killed_str = ' and '.join(str(n) for n in tonight_died)
                print(t('witch_notice_killed', a=tonight_died[0], b=tonight_died[1]))

            # good potion
            if witch_good and tonight_died:
                a = input(t('witch_use_good_prompt'))
                while a not in ('y', 'n'):
                    a = input(t('please_type_again'))
                if a == 'y':
                    choice = input_int(t('which_player_save'), valid_set=set(tonight_died))
                    tonight_died.remove(choice)
                    logging.info(t('player_saved_by_witch', n=choice))
                    witch_good = False

            # bad potion
            if witch_bad:
                a = input(t('witch_use_bad_prompt'))
                while a not in ('y', 'n'):
                    a = input(t('please_type_again'))
                if a == 'y':
                    # can kill someone not already in tonight_died
                    excluded = set(tonight_died)
                    valid = set(i+1 for i, r in enumerate(player) if r != '') - excluded
                    if not valid:
                        print(t('no_valid_targets'))
                    else:
                        choice = input_int(t('which_player_kill_witch'), valid_set=valid)
                        tonight_died.append(choice)
                        logging.info(t('player_killed_by_witch', n=choice))
                        witch_bad = False
            clear_screen()


def prophet():
    global player
    if "Prophet" in player:
        time.sleep(1)
        a = input_int(t('who_prophesy'))
        # reveal the role to the prophet (and log it)
        role = player[a-1]
        print(role)
        logging.info(t('player_prophesyed', n=a))
        time.sleep(1)
        clear_screen()


def vote():
    global player, died
    votes = [0] * len(player)
    for i in range(len(player)):
        if player[i] != '':
            a = input_int(t('who_vote'), valid_set=set(j+1 for j, r in enumerate(player) if r != ''))
            votes[a-1] += 1
            clear_screen()
            time.sleep(1)
    max_votes = max(votes)
    # pick the first player with max votes (original behavior)
    victim = votes.index(max_votes)
    # mark player as dead
    player[victim] = ''
    died.append(victim+1)
    print(t('player_out', n=victim+1))
    logging.info(t('player_out', n=victim+1))


# game setup
player = []
died = []
character = ["Civilian", "Civilian", "Werewolf", "Werewolf", "Witch", "Prophet"]

# assign roles randomly
for i in range(6):
    role = character.pop(random.randint(0, len(character)-1))
    player.append(role)
    print(t('you_are', n=i+1, role=role))
    logging.info(f"Player {i+1} is {role}.")
    time.sleep(1)
    clear_screen()

# main game loop
while ("Civilian" in player) and ("Werewolf" in player) and (("Witch" in player) or ("Prophet" in player)):
    tonight_died = []
    werewolf()
    witch()
    prophet()

    # apply tonight deaths
    # remove duplicates and only kill players that are currently alive
    unique_deaths = []
    for idx in tonight_died:
        if 1 <= idx <= len(player) and player[idx-1] != '' and idx not in unique_deaths:
            unique_deaths.append(idx)

    for i in unique_deaths:
        print(t('tonight_killed', n=i))
        logging.info(t('tonight_killed', n=i))
        player[i-1] = ''
        died.append(i)

    vote()

# game end
if ("Civilian" not in player) or (("Witch" not in player) and ("Prophet" not in player)):
    print(t('werewolves_win'))
    logging.info(t('werewolves_win'))
else:
    print(t('civilians_win'))
    logging.info(t('civilians_win'))
