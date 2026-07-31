"""Agentic solver for the guessing game.

The agent plays the game on its own: it plans a guess, submits it, reads the
hint the game gives back, narrows its search range, and then checks that the
narrowed range still describes a number that could exist. It keeps a
step-by-step log and a confidence score so you can see its reasoning instead of
just the answer.
"""

from dataclasses import dataclass

from logic_utils import check_guess, guesses_for_range


@dataclass
class Step:
    attempt: int
    guess: int
    outcome: str
    low: int
    high: int
    confidence: float
    note: str = ""


class GuessingAgent:
    def __init__(self, low, high, max_attempts=None):
        # full range for this round, and the range the agent still considers
        # possible as it learns from hints
        self.low = low
        self.high = high
        self.lo = low
        self.hi = high
        # A cap always applies. Left as None it used to mean "no limit", so a
        # judge the agent couldn't understand kept the loop running forever.
        if max_attempts is None:
            max_attempts = guesses_for_range(high - low + 1)
        self.max_attempts = max_attempts
        self.attempt = 0
        self.status = "playing"  # playing / won / lost / stuck
        self.log = []

    def plan(self):
        # Binary search: the midpoint of the remaining range cuts the number
        # of possibilities roughly in half every time.
        return (self.lo + self.hi) // 2

    def confidence(self):
        # How much of the original range the agent has ruled out so far.
        # Starts near 0, reaches 1.0 once only the answer is left.
        span = self.hi - self.lo + 1
        full = self.high - self.low + 1
        if full <= 1:
            return 1.0
        # Once the bounds cross, span drops to zero and this climbs past 1.0.
        # Nothing is more ruled out than everything, so cap it.
        ruled_out = 1 - (span - 1) / (full - 1)
        return round(min(ruled_out, 1.0), 2)

    def revise(self, guess, outcome):
        if outcome == "Too High":
            self.hi = guess - 1
        elif outcome == "Too Low":
            self.lo = guess + 1

    def _hints_are_consistent(self):
        # If the low bound passes the high bound, the hints we've been given
        # can't all be true at once (this is what happens when the game lies,
        # e.g. the original backwards-hint bug).
        return self.lo <= self.hi

    def step(self, secret, judge=check_guess):
        """Play one turn against a judge that returns (outcome, message)."""
        if self.status != "playing":
            # The round is over. Stepping again would keep inflating the
            # attempt count that the app and the harness both report.
            return self.log[-1]

        guess = self.plan()
        self.attempt += 1
        outcome, message = judge(guess, secret)
        self.revise(guess, outcome)

        note = ""
        confidence = self.confidence()
        if outcome == "Win":
            self.status = "won"
            confidence = 1.0
        elif outcome not in ("Too High", "Too Low"):
            # An answer it can't read is as good a reason to stop as a
            # contradiction. Acting on it would mean guessing blind, and
            # revise() would leave the range untouched.
            self.status = "stuck"
            confidence = 0.0
            note = f"judge said {outcome!r}, which I can't read, stopping"
        elif not self._hints_are_consistent():
            # Report no confidence, not full confidence. The range is empty, so
            # "how much have I ruled out" has no honest answer, and showing 1.0
            # here would look identical to a win on the row where it gave up.
            self.status = "stuck"
            confidence = 0.0
            note = "hints contradict each other, stopping"
        elif self.attempt >= self.max_attempts:
            self.status = "lost"

        record = Step(self.attempt, guess, outcome, self.lo, self.hi, confidence, note)
        self.log.append(record)
        return record

    def play(self, secret, judge=check_guess):
        """Play a full game and return the final status."""
        while self.status == "playing":
            self.step(secret, judge)
        return self.status
