import pytest

from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    guesses_for_range,
    guesses_needed,
    parse_guess,
    update_score,
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
# SMALLER range than Normal (making it the easiest). Attempts were backwards
# too (Easy=6, Normal=8, Hard=5), so picking an easier level gave you fewer
# guesses. I retuned them by hand to Easy=8, Normal=6, Hard=5, which fixed the
# ordering but left Normal and Hard unwinnable, because I never checked the
# numbers against the range size. They come from the range now: a harder level
# means a bigger range and less headroom above the guesses that range needs.
# It can't mean fewer attempts outright, because a bigger range needs more.


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


# --- parse_guess and update_score, the two the game leans on hardest ---


def test_parse_guess_rejects_empty_and_junk():
    assert parse_guess("") == (False, None, "Enter a guess.")
    assert parse_guess("abc")[0] is False


def test_parse_guess_reads_plain_numbers():
    assert parse_guess("42") == (True, 42, None)


def test_parse_guess_truncates_decimals():
    # 42.9 becomes 42, so the player is judged on a number they didn't type.
    # Pinning it because the app relies on getting an int back either way.
    assert parse_guess("42.9") == (True, 42, None)


def test_parse_guess_does_not_check_the_range():
    # It only guards the format. app.py is what keeps an out-of-range guess
    # from reaching the game.
    assert parse_guess("999999") == (True, 999999, None)


def test_winning_early_scores_more_than_winning_late():
    assert update_score(0, "Win", 1) > update_score(0, "Win", 5)


def test_score_never_drops_below_ten_for_a_win():
    assert update_score(0, "Win", 99) == 10


def test_every_wrong_guess_costs_the_same():
    assert update_score(100, "Too High", 1) == 95
    assert update_score(100, "Too Low", 4) == 95


def test_guesses_for_range_rejects_an_empty_range():
    # match= matters: without it, math.log2(0) raising on its own would pass.
    with pytest.raises(ValueError, match="at least one number"):
        guesses_for_range(0)


def test_guesses_for_range_on_a_power_of_two():
    # The whole reason for floor+1 over ceil. 64 really needs 7.
    assert guesses_for_range(64) == 7
