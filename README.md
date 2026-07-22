# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [X] Describe the game's purpose. 
   The game's purpose is a number-guessing game as the application picks a secret number within a range based on difficulty (Easy 1-20, Normal 1-100, Hard 1-200), and the player has limited attempts to guess the secret number. After each guess, the game gives a Higher or Lower hint and updates the player score. 

- [X] Detail which bugs you found. 
   I found a state bug where the secret number didn't stay constant across user submissions as it was changing on alternate attempts as it was cast to a string. The constant changing broke the comparisons. I found a logic bug as the higher/lower hints were reversed and unreliable most of the time so I had to fix the output labels. I also found a scoring bug as a too high guess had the possibility of adding points on even attempts instead of always reducing the score every time the user had an incorrect guess. 

- [X] Explain what fixes you applied. 
   I made sure that the secret number was fixed as a single "int" (not being converted to string) for the entire round so there was no type switching or resets between each user guess submission. I applied a fix where check_guess was rewritten to compare numbers directly so that the higher/lower hints are always correct and the game is winnable. I applied a fix where the scoring system was correct so that wrong guesses consistently reduce the user score. I applied a fix where the game logic was refactored into logic_utils_py and was verified with pytest. 

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. User enters a guess of 40 -> Game Returns "Too Low" -> hint: Go HIGHER! -->
2. User enters a guess of 70 -> Game returns "Too High" -> hint: Go LOWER! -->
3. User enters a guess of 55 -> Game Returns "Too Low" -> hint: Go HIGHER! -->
4. User enters a guess of 63 -> Game returns "Win" -> Correct! -->
5. Score updates after every guess and the game ends on the correct guess, showing secret and final score. -->

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ pytest
========================= test session starts =========================
collected 8 items

tests/test_game_logic.py ........                                [100%]

========================== 8 passed in 0.79s ==========================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
