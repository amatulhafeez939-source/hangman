#!/usr/bin/env python3
"""Hangman - console game with ASCII gallows art.

Run:   python3 hangman.py        (or ./hangman.py after `chmod +x hangman.py`)

Word source (in order):
  1. 'words.txt' next to this script (one word per line, any English list).
  2. The built-in WORDS array below, if words.txt is missing.
"""

import os
import random
import sys

MAX_MISTAKES = 6
WIDTH = 44

# Built-in secret-word array (fallback when words.txt is not found).
WORDS = """
abandon academy account adventure airplane alphabet ancient animal anxious
apple arrow athlete balance banana basket battery beautiful bicycle biscuit
blanket bridge brother butterfly cabinet calendar camera candle captain
carpet castle chicken chimney chocolate circle climate clothes coffee compass
computer cottage cricket crystal curtain dancer daughter desert diamond
dinner doctor dolphin dragon eagle elephant engine evening factory farmer
feather festival finger flower forest fountain friend galaxy garden giraffe
glacier guitar hammer harvest helmet history holiday hospital hungry iceberg
island jacket jungle kangaroo kitchen ladder lantern leather library lizard
machine magnet market meadow mirror monster mountain museum mystery napkin
needle notebook ocean orange origin oyster painter palace parrot pencil
penguin pepper picture pillow pioneer planet pocket puzzle pyramid python
rabbit rainbow rescue river rocket sailor salmon school science shadow silver
skeleton sketch spider squirrel station stomach storm student summer sunrise
sunshine teacher telephone thunder ticket tiger tomato tonight tornado
tractor travel treasure triangle trumpet tunnel turtle umbrella universe
valley village violin volcano walnut waterfall weather window winter wizard
yellow zebra
""".split()

# One ASCII gallows picture per number of mistakes (0-6).
STAGES = [
    r"""
      +---+
      |   |
          |
          |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
          |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
     /    |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
     / \  |
          |
    =========""",
]

# The hangman escapes: shown on the victory screen.
FREED = r"""
              \O/
               |
              / \
    ===================="""

DIFFICULTY = {
    "1": ("Easy", 4, 5),
    "2": ("Medium", 6, 8),
    "3": ("Hard", 9, 30),
}


# ----------------------------------------------------------------- colors --
# Colors are used only in a real terminal (and switched off if NO_COLOR is set).
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
if USE_COLOR and os.name == "nt":
    os.system("")  # lets Windows terminals understand color codes

CODES = {"bold": "1", "red": "31", "green": "32", "yellow": "33",
         "magenta": "35", "cyan": "36"}


def paint(text, *styles):
    """Wrap text in terminal color codes, e.g. paint('Hi', 'green', 'bold')."""
    if not USE_COLOR:
        return text
    return f"\033[{';'.join(CODES[s] for s in styles)}m{text}\033[0m"


# ---------------------------------------------------------------- helpers --
def clear_screen():
    """Clear the terminal (only when running in a real terminal)."""
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def box(lines, char="*"):
    """Return text lines wrapped in a bordered box."""
    edge = char * WIDTH
    out = [edge]
    for line in lines:
        out.append(f"{char} {line.center(WIDTH - 4)} {char}")
    out.append(edge)
    return "\n".join(out)


def load_words():
    """Load words from words.txt if present, otherwise use the WORDS array."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            words = [w.strip().lower() for w in f]
        words = [w for w in words if w.isalpha() and len(w) >= 4]
        if words:
            return words
    return WORDS


def mask_word(word, correct):
    """Return the word with unguessed letters hidden, e.g. '_ A _ H O N'."""
    return " ".join(ch.upper() if ch in correct else "_" for ch in word)


def is_solved(word, correct):
    return all(ch in correct for ch in word)


# ----------------------------------------------------------------- screens --
def title_screen():
    clear_screen()
    print(paint(box(["H A N G M A N", "", "Guess the word before the",
                     "hangman is complete!"]), "cyan", "bold"))
    print()


def choose_difficulty():
    print("Choose difficulty:")
    print("  1) Easy    (4-5 letters)")
    print("  2) Medium  (6-8 letters)")
    print("  3) Hard    (9+ letters)")
    while True:
        choice = input("Enter 1, 2 or 3 [2]: ").strip() or "2"
        if choice in DIFFICULTY:
            return DIFFICULTY[choice]
        print("Please enter 1, 2 or 3.")


def game_screen(secret, correct, wrong, message=None):
    """Draw the board. message is a (text, color) pair or None."""
    clear_screen()
    print(paint(box(["H A N G M A N"]), "cyan", "bold"))
    print(paint(STAGES[len(wrong)], "yellow"))
    print()
    print("  Word:   ", paint(mask_word(secret, correct), "cyan", "bold"))
    wrong_text = " ".join(sorted(wrong)).upper() or "-"
    print("  Wrong:  ", paint(wrong_text, "red"))
    left = MAX_MISTAKES - len(wrong)
    print("  Lives:  ", paint("<3 " * left, "red"), f"({left} left)")
    print()
    if message:
        text, color = message
        print("  " + paint(text, color, "bold") + "\n")


def victory_screen(secret, wrong):
    clear_screen()
    print(paint(box(["", "V I C T O R Y !", "", "You saved the hangman!", ""]),
                "green", "bold"))
    print(paint(FREED, "green"))
    print()
    print(f"  The word was:  {paint(secret.upper(), 'green', 'bold')}")
    print(f"  Mistakes made: {len(wrong)} of {MAX_MISTAKES}")
    print()


def defeat_screen(secret, correct):
    clear_screen()
    print(paint(box(["", "G A M E   O V E R", "",
                     "The hangman didn't make it...", ""]), "red", "bold"))
    print(paint(STAGES[MAX_MISTAKES], "red"))
    print()
    print(f"  You had:       {mask_word(secret, correct)}")
    print(f"  The word was:  {paint(secret.upper(), 'red', 'bold')}")
    print()


# -------------------------------------------------------------------- game --
def get_guess(correct, wrong):
    """Ask until the player types a single new letter."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("  Please enter a single letter (a-z).")
        elif guess in correct or guess in wrong:
            print(f"  You already tried '{guess}'. Pick another letter.")
        else:
            return guess


def play(words):
    """Play one round. Returns True on a win, False on a loss."""
    title_screen()
    _name, low, high = choose_difficulty()
    pool = [w for w in words if low <= len(w) <= high] or words
    secret = random.choice(pool)

    correct = set()   # correctly guessed letters
    wrong = set()     # incorrectly guessed letters
    message = (f"The word has {len(secret)} letters. Good luck!", "magenta")

    while True:
        game_screen(secret, correct, wrong, message)

        guess = get_guess(correct, wrong)
        if guess in secret:
            correct.add(guess)
            message = (f"Good guess! '{guess.upper()}' is in the word.", "green")
        else:
            wrong.add(guess)
            message = (f"Sorry, '{guess.upper()}' is not in the word.", "red")

        if is_solved(secret, correct):
            victory_screen(secret, wrong)
            return True
        if len(wrong) >= MAX_MISTAKES:
            defeat_screen(secret, correct)
            return False


def main():
    words = load_words()
    wins = losses = 0
    try:
        while True:
            if play(words):
                wins += 1
            else:
                losses += 1
            print(f"  Score  ->  Wins: {wins}   Losses: {losses}\n")
            if input("Play again? (y/n): ").strip().lower() != "y":
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print("Thanks for playing Hangman!")


if __name__ == "__main__":
    main()
