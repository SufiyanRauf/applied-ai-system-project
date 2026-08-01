from agent import GuessingAgent
from evaluate import lying_judge
from logic_utils import get_range_for_difficulty, guesses_needed


def test_agent_wins_every_normal_game():
    # Binary search should find any secret in the range, no exceptions.
    low, high = get_range_for_difficulty("Normal")
    for secret in range(low, high + 1):
        agent = GuessingAgent(low, high)
        assert agent.play(secret) == "won"


def test_agent_stays_within_binary_search_bound():
    low, high = get_range_for_difficulty("Normal")
    worst_case = guesses_needed("Normal")
    for secret in range(low, high + 1):
        # The cap has to be looser than the bound being checked. Capping at
        # worst_case would make the assertion true by construction, so a much
        # worse strategy would still pass.
        agent = GuessingAgent(low, high, max_attempts=high)
        assert agent.play(secret) == "won"
        assert agent.attempt <= worst_case


def test_confidence_climbs_as_the_range_shrinks():
    # step() hardcodes 1.0 on a win, so asserting on the last row only tests
    # that override. The rows before it are where the formula actually runs.
    # Checked across the whole range, not one secret: an earlier version of this
    # only passed because 73 happened to suit it.
    for secret in range(1, 101):
        agent = GuessingAgent(1, 100)
        agent.play(secret)
        climbing = [s.confidence for s in agent.log[:-1]]
        assert climbing == sorted(climbing)
        if len(climbing) >= 2:
            assert climbing[0] < climbing[-1]


def test_confidence_is_one_on_a_win():
    agent = GuessingAgent(1, 100)
    agent.play(63)
    assert agent.log[-1].confidence == 1.0


def test_confidence_is_zero_when_the_hints_contradict():
    # An empty range means nothing can be trusted, so reporting full confidence
    # here would look exactly like a win.
    agent = GuessingAgent(1, 100, max_attempts=20)
    agent.play(42, judge=lying_judge)
    assert agent.log[-1].confidence == 0.0


def test_guardrail_detects_lying_game():
    # A game that flips its hints should trip the consistency check, and the
    # cap here is loose so it's the check that stops it, not the cap.
    agent = GuessingAgent(1, 100, max_attempts=20)
    status = agent.play(42, judge=lying_judge)
    assert status == "stuck"
    assert "contradict" in agent.log[-1].note


def test_agent_stops_on_an_answer_it_cannot_read():
    # revise() only moves the range for Too High and Too Low, so anything else
    # used to leave the bounds untouched and the loop running forever.
    def broken_judge(guess, secret):
        return "Maybe", "no idea"

    agent = GuessingAgent(1, 100)
    assert agent.play(42, judge=broken_judge) == "stuck"
    assert "can't read" in agent.log[-1].note


def test_agent_always_has_an_attempt_cap():
    # Built without one, it still has to stop on its own.
    assert GuessingAgent(1, 100).max_attempts == 7


def test_first_guess_is_the_midpoint():
    agent = GuessingAgent(1, 100)
    assert agent.plan() == 50


def test_guardrail_catches_every_lying_game_but_the_opening_guess():
    # One secret isn't enough for the project's central claim: an off-by-one in
    # revise() drops this to 49 of 100 while every other test still passes.
    low, high = get_range_for_difficulty("Normal")
    caught = [
        s for s in range(low, high + 1)
        if GuessingAgent(low, high, max_attempts=high).play(s, judge=lying_judge) == "stuck"
    ]
    assert len(caught) == 99
    assert GuessingAgent(low, high).plan() not in caught


def test_agent_gives_up_when_it_runs_out_of_attempts():
    # The only stop condition with no other coverage.
    agent = GuessingAgent(1, 100, max_attempts=3)
    assert agent.play(99) == "lost"
    assert agent.attempt == 3


def test_agent_stops_on_a_judge_that_answers_in_the_wrong_shape():
    agent = GuessingAgent(1, 100)
    assert agent.play(42, judge=lambda g, s: None) == "stuck"
    assert "can't read" in agent.log[-1].note
