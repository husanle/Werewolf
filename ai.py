import logging
import random
import re
from config import client, model, get_provider, TEMPERATURE, TIMEOUT


def parse_numeric_response(response_text, valid_choices):
    """
    Extract a numeric choice from the AI response.
    valid_choices is a set of acceptable player numbers.
    Returns the first valid number found, or None if no valid number.
    """
    # Find all numbers in the response
    numbers = re.findall(r'\d+', response_text)
    for num_str in numbers:
        try:
            num = int(num_str)
            if num in valid_choices:
                return num
        except ValueError:
            continue
    return None


def parse_yesno_response(response_text):
    """
    Extract a yes/no decision from the AI response.
    Returns 'y' or 'n'.
    """
    text = response_text.lower()
    # Check for y or yes
    if 'y' in text or 'yes' in text:
        return 'y'
    # Default to n if no clear yes
    return 'n'


def call_openai(messages, max_tokens=100, max_retries=3):
    """Call OpenAI Chat Completions API."""
    if client is None:
        return None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=max_tokens,
                timeout=TIMEOUT
            )
            content = response.choices[0].message.content.strip()
            return content
        except Exception as e:
            logging.error(f"OpenAI API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None


def call_anthropic(messages, max_tokens=100, max_retries=3):
    """Call Anthropic Messages API."""
    if client is None:
        return None

    # Convert OpenAI-format messages to Anthropic format
    anthropic_messages = []
    system_message = None
    for msg in messages:
        if msg["role"] == "system":
            system_message = msg["content"]
        else:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    for attempt in range(max_retries):
        try:
            if system_message:
                response = client.messages.create(
                    model=model,
                    system=system_message,
                    messages=anthropic_messages,
                    temperature=TEMPERATURE,
                    max_tokens=max_tokens,
                    timeout=TIMEOUT
                )
            else:
                response = client.messages.create(
                    model=model,
                    messages=anthropic_messages,
                    temperature=TEMPERATURE,
                    max_tokens=max_tokens,
                    timeout=TIMEOUT
                )
            content = response.content[0].text.strip()
            return content
        except Exception as e:
            logging.error(f"Anthropic API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None


def call_ai(messages, max_tokens=100, max_retries=3):
    """Generic AI call that dispatches to the configured provider."""
    provider = get_provider()
    logging.info(f"Calling {provider} AI...")

    if provider == "openai":
        response = call_openai(messages, max_tokens, max_retries)
    elif provider == "anthropic":
        response = call_anthropic(messages, max_tokens, max_retries)
    else:
        return None

    if response is not None:
        logging.info(f"AI response: {response}")
    return response


def get_system_prompt():
    """Get the system prompt describing the game."""
    return """You are an AI player playing a game of Werewolf (a social deduction game).
You are playing on a 6-player board with: 2 Werewolves, 2 Civilians, 1 Witch, and 1 Prophet.

Rules summary:
- Werewolves know who the other Werewolves are and kill one player each night
- Witch has one healing potion and one poison potion. She can save a player killed by Werewolves or poison another player
- Prophet can check the role of one player each night
- During the day, all alive players vote to eliminate one player suspected of being a Werewolf
- Werewolves win when all non-Werewolves are dead or there are equal numbers of Werewolves and Villagers
- Villagers (Civilians + Witch + Prophet) win when all Werewolves are eliminated

Your goal: Play strategically to win for your team. Think about the game state and make the best possible move.

Important: Respond ONLY with the answer in the exact format requested. Do not add extra explanation unless asked. For example, if asked to choose a player number, just respond with the number. If asked yes/no, just respond with y or n.
"""


def ai_werewolf_decision(player_num, role, alive_players, dead_players, other_werewolves):
    """
    AI decision for Werewolf night kill.
    Returns the chosen player number to kill.
    """
    logging.info(f"AI Werewolf (player {player_num}) thinking about who to kill...")

    prompt = f"""You are Player {player_num} and your role is Werewolf.

Game State:
- Alive players: {sorted(alive_players)}
- Dead players: {sorted(dead_players)}
- Other werewolves (your teammates): {sorted(other_werewolves)}

As a Werewolf, you must choose which player to kill tonight. You cannot kill other Werewolves.
Valid targets are alive non-Werewolf players.

Respond with ONLY the player number you want to kill.
"""

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": prompt}
    ]

    valid_targets = [p for p in alive_players if p not in other_werewolves]
    valid_set = set(valid_targets)

    response = call_ai(messages, max_tokens=100)
    if response is None:
        # Fallback to random choice
        choice = random.choice(valid_targets)
        logging.info(f"AI fell back to random choice: {choice}")
        return choice

    choice = parse_numeric_response(response, valid_set)
    if choice is not None:
        return choice

    # Fallback to random if parsing failed
    choice = random.choice(valid_targets)
    logging.warning(f"AI parsing failed, fell back to random choice: {choice}")
    return choice


def ai_witch_decision(player_num, role, alive_players, dead_players, tonight_killed, has_heal, has_poison):
    """
    AI decision for Witch actions.
    Returns (use_heal, heal_target, use_poison, poison_target)
    use_heal is 'y' or 'n', use_poison is 'y' or 'n'
    If not used, target is None
    """
    logging.info(f"AI Witch (player {player_num}) thinking about potions...")

    prompt = f"""You are Player {player_num} and your role is Witch.

Game State:
- Alive players: {sorted(alive_players)}
- Dead players: {sorted(dead_players)}
- Players killed by Werewolves tonight: {sorted(tonight_killed)}
- You have a healing potion: {'Yes' if has_heal else 'No'}
- You have a poison potion: {'Yes' if has_poison else 'No'}

First, decide: {'Do you want to use your healing potion on one of the killed players? (answer y/n)' if has_heal else 'No healing potion left.'}
{'If you use healing potion, which player do you want to save?' if has_heal else ''}

Then, decide: {'Do you want to use your poison potion to kill another alive player? (answer y/n)' if has_poison else 'No poison potion left.'}
{'If you use poison, which player do you want to kill?' if has_poison else ''}

Respond in this format: First y/n for healing, then the player number if yes, then y/n for poison, then the player number if yes.
Example: y 3 n → use heal on 3, don't use poison
Example: n y 4 → don't use heal, use poison on 4
Example: y 2 y 5 → use both
Example: n n → use neither
"""

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": prompt}
    ]

    response = call_ai(messages, max_tokens=150)
    if response is None:
        # Fallback: don't use anything
        logging.info("AI fell back: not using any potions")
        return ('n', None, 'n', None)

    # Parse response
    use_heal = 'n'
    heal_target = None
    use_poison = 'n'
    poison_target = None

    numbers = re.findall(r'\d+', response)
    lowered = response.lower()

    # Check for heal
    if has_heal:
        if 'y' in lowered[:20]:  # Check beginning for answer
            use_heal = 'y'
            # First number is heal target
            for num_str in numbers:
                num = int(num_str)
                if num in tonight_killed:
                    heal_target = num
                    break

    # Check for poison
    if has_poison:
        # If we already found heal target, look for next number
        found_heal = heal_target is not None
        valid_poison_targets = [p for p in alive_players if p != player_num and (heal_target is None or p not in tonight_killed)]
        for num_str in numbers:
            num = int(num_str)
            num = int(num_str)
            if num in valid_poison_targets:
                if found_heal:
                    poison_target = num
                    use_poison = 'y'
                    break
                elif num != heal_target:
                    poison_target = num
                    use_poison = 'y'
                break
        if poison_target is None and 'y' in lowered:
            # Try to find any valid
            if valid_poison_targets:
                poison_target = random.choice(valid_poison_targets)
                use_poison = 'y'

    return (use_heal, heal_target, use_poison, poison_target)


def ai_prophet_decision(player_num, role, alive_players, dead_players, previous_checks):
    """
    AI decision for Prophet night check.
    Returns the chosen player number to check.
    """
    logging.info(f"AI Prophet (player {player_num}) thinking about who to check...")

    checks_str = []
    for p, role_revealed in previous_checks.items():
        checks_str.append(f"  Player {p}: {role_revealed}")

    prompt = f"""You are Player {player_num} and your role is Prophet.

Game State:
- Alive players: {sorted(alive_players)}
- Dead players: {sorted(dead_players)}
- Your previous checks:
{chr(10).join(checks_str) if checks_str else '  None'}

As Prophet, you can check the role of any one alive player who you haven't checked yet.
Choose which player to check.

Respond with ONLY the player number you want to check.
"""

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": prompt}
    ]

    valid_targets = [p for p in alive_players if p not in previous_checks]
    valid_set = set(valid_targets)

    response = call_ai(messages, max_tokens=100)
    if response is None:
        choice = random.choice(valid_targets)
        logging.info(f"AI fell back to random choice: {choice}")
        return choice

    choice = parse_numeric_response(response, valid_set)
    if choice is not None:
        return choice

    choice = random.choice(valid_targets)
    logging.warning(f"AI parsing failed, fell back to random choice: {choice}")
    return choice


def ai_vote_decision(player_num, role, alive_players, dead_players, vote_history, known_roles=None):
    """
    AI decision for daytime voting.
    Returns the chosen player number to vote for.
    """
    logging.info(f"AI Player {player_num} thinking about who to vote...")

    if known_roles is None:
        known_roles = {}

    history_str = []
    for day, votes in vote_history.items():
        for voter, target in votes:
            history_str.append(f"  Day {day}: Player {voter} voted for Player {target}")

    known_str = []
    for p, r in known_roles.items():
        known_str.append(f"  Player {p}: {r}")

    prompt = f"""You are Player {player_num} and your role is {role}.

Game State:
- Alive players: {sorted(alive_players)}
- Dead players: {sorted(dead_players)}
- Known roles from previous checks:
{chr(10).join(known_str) if known_str else '  None'}
- Voting history from previous days:
{chr(10).join(history_str) if history_str else '  None'}

It's daytime, all alive players vote to eliminate one player suspected of being a Werewolf.
You must vote for one alive player (cannot vote for yourself).

Respond with ONLY the player number you want to vote for.
"""

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": prompt}
    ]

    valid_targets = [p for p in alive_players if p != player_num]
    valid_set = set(valid_targets)

    response = call_ai(messages, max_tokens=100)
    if response is None:
        choice = random.choice(valid_targets)
        logging.info(f"AI fell back to random choice: {choice}")
        return choice

    choice = parse_numeric_response(response, valid_set)
    if choice is not None:
        return choice

    choice = random.choice(valid_targets)
    logging.warning(f"AI parsing failed, fell back to random choice: {choice}")
    return choice
