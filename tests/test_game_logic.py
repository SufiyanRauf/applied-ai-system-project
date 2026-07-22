from app import attempt_limit_map, check_guess, get_range_for_difficulty


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
    # App stringifies the secret on even attempts, exercising the
    # except TypeError fallback in check_guess.
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


def test_attempts_shrink_with_difficulty():
    # Harder difficulty => fewer (or equal, never more) attempts.
    assert (
        attempt_limit_map["Easy"]
        >= attempt_limit_map["Normal"]
        >= attempt_limit_map["Hard"]
    )
    # And the extremes must be strictly ordered: Easy gives more than Hard.
    assert attempt_limit_map["Easy"] > attempt_limit_map["Hard"]
