from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    guesses_needed,
)


def test_winning_guess():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high_says_go_lower():
    # Guess is above the secret -> player must go LOWER.
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_guess_too_low_says_go_higher():
    # Guess is below the secret -> player must go HIGHER.
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message
    assert "LOWER" not in message


def test_too_high_hint_direction_string_secret():
    # check_guess coerces with int(), so a string secret still compares as a
    # number. The app no longer passes one, but nothing stops another caller.
    outcome, message = check_guess(60, "50")
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_too_low_hint_direction_string_secret():
    outcome, message = check_guess(40, "50")
    assert outcome == "Too Low"
    assert "HIGHER" in message
    assert "LOWER" not in message


# --- Regression tests for the "difficulty is backwards" bug ---
#
# The original code had Easy=1..20, Normal=1..100, Hard=1..50, so Hard had a
# SMALLER range than Normal (making it the easiest). Attempts were also
# inconsistent (Easy=6, Normal=8, Hard=5). A harder level must mean a bigger
# guessing range AND fewer attempts.


def _range_size(difficulty):
    low, high = get_range_for_difficulty(difficulty)
    return high - low + 1


def test_range_grows_with_difficulty():
    # Harder difficulty => strictly bigger guessing range.
    assert _range_size("Easy") < _range_size("Normal") < _range_size("Hard")


def test_hard_range_is_larger_than_normal():
    # The exact original bug: Hard's upper bound was below Normal's.
    _, hard_high = get_range_for_difficulty("Hard")
    _, normal_high = get_range_for_difficulty("Normal")
    assert hard_high > normal_high


def test_every_difficulty_is_winnable():
    # The old limits (Easy 8, Normal 6, Hard 5) made Normal and Hard impossible
    # to win even playing perfectly, because they were picked by hand instead of
    # from the range. Perfect play has to fit inside the limit.
    for difficulty in ("Easy", "Normal", "Hard"):
        assert get_attempt_limit(difficulty) >= guesses_needed(difficulty)


def test_headroom_shrinks_with_difficulty():
    # Harder can't mean fewer guesses, since the range grows. What shrinks is
    # the slack you get above the minimum.
    def headroom(difficulty):
        return get_attempt_limit(difficulty) - guesses_needed(difficulty)

    assert headroom("Easy") > headroom("Normal") > headroom("Hard")
