import random

import streamlit as st

from agent import GuessingAgent
from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    guesses_needed,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Debugged, tested, and now it plays itself.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

low, high = get_range_for_difficulty(difficulty)
attempt_limit = get_attempt_limit(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Switching difficulty has to start a fresh round, otherwise the old secret can
# sit outside the new range and the game (or the AI solver) gets stuck on a
# number that isn't even possible anymore.
if "difficulty" not in st.session_state:
    st.session_state.difficulty = difficulty

if st.session_state.difficulty != difficulty:
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # Full reset: a new round has to clear the score, status, and history and
    # pick the secret from the *current* difficulty range, not always 1-100.
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

st.divider()
st.subheader("🤖 AI Auto-Solver")
st.caption(
    "Let the agent play this round on its own. It halves the range on every "
    "guess, reads the hint, and checks the hints stay consistent before "
    "trusting them."
)

if st.button("Watch the AI play 👀"):
    solver = GuessingAgent(low, high, max_attempts=guesses_needed(difficulty))
    solver.play(st.session_state.secret)

    st.table([
        {
            "Attempt": s.attempt,
            "Guess": s.guess,
            "Hint": s.outcome,
            "Range left": f"{s.low}-{s.high}",
            "Confidence": s.confidence,
        }
        for s in solver.log
    ])

    if solver.status == "won":
        st.success(
            f"The agent found {st.session_state.secret} in "
            f"{solver.attempt} guesses."
        )
    elif solver.status == "stuck":
        st.error("The agent stopped: the hints contradicted each other.")
    else:
        st.warning("The agent used up its attempt budget without winning.")

st.divider()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        # Input that never reached the game shouldn't cost an attempt, and it
        # used to: the counter was incremented before the guess was parsed, so
        # typing junk could push "attempts left" negative without ever ending
        # the round.
        st.error(err)
    elif not low <= guess_int <= high:
        st.error(f"Guess a number between {low} and {high}.")
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: Pass the int secret straight to check_guess (removed the
        # even-attempt str() conversion) so hints compare numbers, not
        # strings. Refactored with AI in agent mode.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
