"""Reliability harness for the guessing agent.

Runs the agent across a whole range of secret numbers and prints a summary so
you can see how it performs without playing by hand. It also runs a guardrail
check: when the game gives dishonest hints, the agent should notice and stop
instead of looping forever.

Run it with:  python evaluate.py
"""

from agent import GuessingAgent
from logic_utils import check_guess, get_range_for_difficulty, guesses_needed


def lying_judge(guess, secret):
    """A broken game that flips its hints, like the original backwards bug."""
    outcome, message = check_guess(guess, secret)
    if outcome == "Too High":
        return "Too Low", message
    if outcome == "Too Low":
        return "Too High", message
    return outcome, message


def run_range(difficulty):
    low, high = get_range_for_difficulty(difficulty)
    worst_case = guesses_needed(difficulty)

    results = []
    for secret in range(low, high + 1):
        agent = GuessingAgent(low, high, max_attempts=worst_case)
        agent.play(secret)
        results.append(agent)

    wins = [a for a in results if a.status == "won"]
    attempts = [a.attempt for a in wins]
    win_confidence = [a.log[-1].confidence for a in wins]

    print(f"Difficulty: {difficulty}  (range {low}-{high})")
    print(f"  Games played:     {len(results)}")
    print(f"  Wins:             {len(wins)}/{len(results)}")
    print(f"  Avg attempts:     {sum(attempts) / len(attempts):.2f}")
    print(f"  Worst attempts:   {max(attempts)} (theoretical cap {worst_case})")
    print(f"  Avg confidence:   {sum(win_confidence) / len(win_confidence):.2f}")
    return len(wins) == len(results) and max(attempts) <= worst_case


def run_guardrail_check():
    low, high = get_range_for_difficulty("Normal")
    agent = GuessingAgent(low, high, max_attempts=20)
    agent.play(42, judge=lying_judge)

    print("Guardrail check: agent vs. a game that lies")
    print(f"  Final status:     {agent.status}")
    print(f"  Note:             {agent.log[-1].note or '(none)'}")
    return agent.status == "stuck"


def main():
    print("=" * 55)
    print("Guessing Agent - Reliability Report")
    print("=" * 55)

    checks = []
    for difficulty in ("Easy", "Normal", "Hard"):
        checks.append(run_range(difficulty))
        print()

    guardrail_ok = run_guardrail_check()
    checks.append(guardrail_ok)
    print()

    passed = sum(checks)
    print("=" * 55)
    print(f"Summary: {passed}/{len(checks)} checks passed")
    if guardrail_ok:
        print("The agent solves every honest game and safely stops on a liar.")
    print("=" * 55)


if __name__ == "__main__":
    main()
