"""Prints the three sample runs from the README.

I use this to check the agent still behaves the same after I change something,
and the output is what I pasted into the README as the example interactions.

Run it with:  python3 demo.py
"""

from agent import GuessingAgent
from evaluate import lying_judge
from logic_utils import parse_guess


def print_log(agent, show_confidence=True):
    for s in agent.log:
        rng = f"{s.low}-{s.high}"
        line = f"  attempt {s.attempt}: guessed {s.guess:3d} -> {s.outcome:10}range now {rng:6}"
        if show_confidence:
            line += f" confidence {s.confidence}"
        if s.note:
            line += f"  {s.note}"
        print(line.rstrip())


def normal_round(secret=63):
    print(f"secret = {secret}, range 1-100")
    agent = GuessingAgent(1, 100)
    agent.play(secret)
    print_log(agent)
    print(f"status: {agent.status}")


def lying_round(secret=42):
    print(f"lying game, secret = {secret}")
    # A loose cap on purpose, so it's the guardrail that stops this run and not
    # the cap. The agent always has a cap now, so nothing can hang either way.
    agent = GuessingAgent(1, 100, max_attempts=20)
    agent.play(secret, judge=lying_judge)
    print_log(agent, show_confidence=False)
    print(f"status: {agent.status}")


def bad_input():
    for raw in ["", "abc", "42", "42.9"]:
        call = f'parse_guess("{raw}")'
        print(f"{call:22} -> {parse_guess(raw)}")


def main():
    print("1. The agent solves a normal round")
    print()
    normal_round()

    print()
    print("2. The guardrail catches a game that lies")
    print()
    lying_round()

    print()
    print("3. Bad input is rejected before it reaches the game")
    print()
    bad_input()


if __name__ == "__main__":
    main()
