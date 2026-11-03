# Task: Hangman (Console Game)

A colorful command-line Hangman game written in pure Python 3 (standard library only).

## How to run

```bash
cd task1_hangman
python hangman.py        # on Mac/Linux: python3 hangman.py
```

Keep `hangman.py` and `words.txt` in the same folder.

## Rules

- The computer picks a secret word; you see it masked, e.g. `P _ T H O _`.
- Type one letter per turn.
- A correct letter is revealed everywhere it appears.
- A wrong letter costs one life and adds a part to the ASCII gallows.
- You have **6 mistakes**. Guess the word before the drawing is complete to win.

## Features

- Secret word chosen with `random.choice()`
- Correctly guessed letters tracked in a `set`
- Masked word display (`_ A _ H O N`)
- 7 stages of ASCII gallows art (0 to 6 mistakes)
- Clean boxed **Victory** and **Game Over** screens
- Difficulty levels: Easy (4-5 letters), Medium (6-8), Hard (9+)
- Word list loaded from `words.txt` (8,810 usable English words); falls back to a built-in `WORDS` array if the file is missing
- Input validation (single letters only, no repeated guesses)
- Colored output in a real terminal (disabled automatically if unsupported or `NO_COLOR` is set)
- Win/loss score and "play again" option

## Files

| File | Purpose |
|------|---------|
| `hangman.py` | The game |
| `words.txt` | English word list (one word per line) |

## Requirements

Python 3 only. No extra packages.
