import random
import time
import os
import logging
import sys
from lang import load, t
from config import is_configured, get_provider
import ai

# cross-platform clear
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# choose language from --lang argument or LANG environment
lang_arg = None
if '--lang=' in sys.argv:
    idx = [i for i, arg in enumerate(sys.argv) if arg.startswith('--lang=')][0]
    lang_arg = sys.argv[idx].split('=', 1)[1]
else:
    env = os.environ.get('LANG', '')
    if env:
        lang_arg = env[:2]

load(lang_arg or 'en')

# parse --ai argument: --ai=1,2,3
ai_players_arg = None
ai_player_numbers = []
for arg in sys.argv:
    if arg.startswith('--ai='):
        ai_players_arg = arg.split('=', 1)[1]
        try:
            ai_player_numbers = [int(x.strip()) for x in ai_players_arg.split(',') if x.strip()]
        except ValueError:
            pass
        break

# configure logging to log.txt with utf-8 encoding
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')
logging.info(t('game_start', time=time.strftime("%Y-%m-%d %H:%M:%S")))

# Check if AI provider is configured
if not is_configured():
    provider = get_provider()
    if provider == "openai":
        print(t('openai_not_configured'))
        logging.info(t('openai_not_configured'))
    else:
        print(f"{provider.upper()} API key not configured. AI players will fall back to random choices.")
        logging.info(f"{provider.upper()} API key not configured. AI players will fall back to random choices.")

witch_good = True
witch_bad = True
player = []
# Track which players are AI (1-based index, is_ai[0] is player 1)
is_ai = [False] * 6
# Track prophet checks for AI
prophet_checks = {}
# Track vote history for AI
vote_history = {}


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


# helper for yes/no input
def input_yesno(prompt):
    while True:
        a = input(prompt)
        a = a.strip().lower()
        if a in ('y', 'n'):
            return a
        print(t('please_type_again'))


def get_alive_players():
    """Get list of alive player numbers (1-based)."""
    return [i + 1 for i, r in enumerate(player) if r != '']


def get_dead_players():
    """Get list of dead player numbers (1-based)."""
    return died


def werewolf():
    global player, tonight_died
    # Get all alive werewolves
    alive_werewolves = []
    for i, role in enumerate(player):
        if role == 'werewolf':
            alive_werewolves.append(i + 1)  # 1-based

    for werewolf_num in alive_werewolves:
        if len(tonight_died) >= len(alive_werewolves):
            # Already got enough kills
            break

        other_werewolves = [w for w in alive_werewolves if w != werewolf_num]
        alive_players = get_alive_players()

        if is_ai[werewolf_num - 1]:
            # AI werewolf
            print(t('ai_thinking', n=werewolf_num))
            valid_targets = [p for p in alive_players if p not in alive_werewolves]
            if not valid_targets:
                continue
            choice = ai.ai_werewolf_decision(
                player_num=werewolf_num,
                role='werewolf',
                alive_players=alive_players,
                dead_players=get_dead_players(),
                other_werewolves=other_werewolves
            )
            print(t('ai_chose', n=werewolf_num, choice=choice))
            logging.info(t('werewolf_killed', n=choice))
            logging.info(t('ai_chose', n=werewolf_num, choice=choice))
            if choice not in tonight_died:
                tonight_died.append(choice)
            time.sleep(1)
            clear_screen()
        else:
            # Human werewolf
            killed_player = input_int(t('who_kill'))
            logging.info(t('werewolf_killed', n=killed_player))
            clear_screen()
            if killed_player not in tonight_died:
                tonight_died.append(killed_player)
            time.sleep(1)


def witch():
    global player, witch_good, witch_bad
    # Find which player is witch
    witch_idx = None
    for i, role in enumerate(player):
        if role == 'witch':
            witch_idx = i
            break
    if witch_idx is None:
        return

    witch_num = witch_idx + 1
    alive_players = get_alive_players()
    dead_players = get_dead_players()

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

        if is_ai[witch_num - 1]:
            # AI witch
            print(t('ai_thinking', n=witch_num))
            use_heal, heal_target, use_poison, poison_target = ai.ai_witch_decision(
                player_num=witch_num,
                role='witch',
                alive_players=alive_players,
                dead_players=dead_players,
                tonight_killed=tonight_died,
                has_heal=witch_good,
                has_poison=witch_bad
            )
            print(t('ai_chose', n=witch_num, choice=f"{use_heal} {heal_target or ''} {use_poison} {poison_target or ''}"))
            logging.info(t('ai_chose', n=witch_num, choice=f"{use_heal} {heal_target or ''} {use_poison} {poison_target or ''}"))

            # Apply healing
            if use_heal == 'y' and witch_good and heal_target in tonight_died:
                tonight_died.remove(heal_target)
                logging.info(t('player_saved_by_witch', n=heal_target))
                witch_good = False

            # Apply poison
            if use_poison == 'y' and witch_bad and poison_target is not None:
                excluded = set(tonight_died)
                valid = set(i+1 for i, r in enumerate(player) if r != '') - excluded
                if poison_target in valid:
                    if poison_target not in tonight_died:
                        tonight_died.append(poison_target)
                    logging.info(t('player_killed_by_witch', n=poison_target))
                    witch_bad = False

            time.sleep(1)
            clear_screen()
            return

        # Human witch
        # good potion
        if witch_good and tonight_died:
            a = input_yesno(t('witch_use_good_prompt'))
            if a == 'y':
                choice = input_int(t('which_player_save'), valid_set=set(tonight_died))
                tonight_died.remove(choice)
                logging.info(t('player_saved_by_witch', n=choice))
                witch_good = False

        # bad potion
        if witch_bad:
            a = input_yesno(t('witch_use_bad_prompt'))
            if a == 'y':
                # can kill someone not already in tonight_died
                excluded = set(tonight_died)
                valid = set(i+1 for i, r in enumerate(player) if r != '') - excluded
                if not valid:
                    print(t('no_valid_targets'))
                else:
                    choice = input_int(t('which_player_kill_witch'), valid_set=valid)
                    if choice not in tonight_died:
                        tonight_died.append(choice)
                    logging.info(t('player_killed_by_witch', n=choice))
                    witch_bad = False
        clear_screen()


def prophet():
    global player, prophet_checks
    # Find which player is prophet
    prophet_idx = None
    for i, role in enumerate(player):
        if role == 'prophet':
            prophet_idx = i
            break
    if prophet_idx is None:
        return

    prophet_num = prophet_idx + 1
    alive_players = get_alive_players()
    dead_players = get_dead_players()

    time.sleep(1)

    if is_ai[prophet_num - 1]:
        # AI prophet
        print(t('ai_thinking', n=prophet_num))
        choice = ai.ai_prophet_decision(
            player_num=prophet_num,
            role='prophet',
            alive_players=alive_players,
            dead_players=dead_players,
            previous_checks=prophet_checks
        )
        print(t('ai_chose', n=prophet_num, choice=choice))
        logging.info(t('player_prophesyed', n=choice))
        logging.info(t('ai_chose', n=prophet_num, choice=choice))
        # reveal the role to AI (store for future)
        role_revealed = player[choice - 1]
        prophet_checks[choice] = role_revealed
        print(role_revealed)
        time.sleep(1)
        clear_screen()
        return

    # Human prophet
    a = input_int(t('who_prophesy'))
    # reveal the role to the prophet (and log it)
    role = player[a-1]
    prophet_checks[a] = role
    print(role)
    logging.info(t('player_prophesyed', n=a))
    time.sleep(1)
    clear_screen()


def vote():
    global player, died
    global vote_history
    day_number = len(died) + 1
    votes = [0] * len(player)
    current_votes = []

    for i in range(len(player)):
        if player[i] != '':
            player_num = i + 1
            role = player[i]
            alive_players = get_alive_players()
            dead_players = get_dead_players()

            # Get known roles (from prophet checks)
            known_roles = {}
            for p_num, r in prophet_checks.items():
                if player[p_num - 1] != '':  # still alive
                    known_roles[p_num] = r

            if is_ai[player_num - 1]:
                # AI vote
                print(t('ai_thinking', n=player_num))
                choice = ai.ai_vote_decision(
                    player_num=player_num,
                    role=role,
                    alive_players=alive_players,
                    dead_players=dead_players,
                    vote_history=vote_history,
                    known_roles=known_roles
                )
                print(t('ai_chose', n=player_num, choice=choice))
                logging.info(t('ai_chose', n=player_num, choice=choice))
                a = choice
            else:
                # Human vote
                a = input_int(t('who_vote'), valid_set=set(j+1 for j, r in enumerate(player) if r != ''))

            votes[a-1] += 1
            current_votes.append((player_num, a))
            clear_screen()
            time.sleep(1)

    # Save vote history
    vote_history[day_number] = current_votes

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
character = ["civilian", "civilian", "werewolf", "werewolf", "witch", "prophet"]

# assign roles randomly
for i in range(6):
    role = character.pop(random.randint(0, len(character)-1))
    player.append(role)
    print(t('you_are', n=i+1, role=role))
    logging.info(f"Player {i+1} is {t(role)}.")
    time.sleep(1)
    clear_screen()

# Configure which players are AI
if ai_player_numbers:
    # From command line argument
    for n in ai_player_numbers:
        if 1 <= n <= 6:
            is_ai[n - 1] = True
else:
    # Interactive configuration
    for i in range(6):
        player_num = i + 1
        ans = input_yesno(t('ask_ai_player', n=player_num))
        if ans == 'y':
            is_ai[i] = True
        clear_screen()

# Log AI configuration
for i in range(6):
    if is_ai[i]:
        logging.info(f"Player {i+1} is AI.")

# main game loop
while ("civilian" in player) and ("werewolf" in player) and (("witch" in player) or ("prophet" in player)):
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
if ("civilian" not in player) or (("witch" not in player) and ("prophet" not in player)):
    print(t('werewolves_win'))
    logging.info(t('werewolves_win'))
else:
    print(t('civilians_win'))
    logging.info(t('civilians_win'))
