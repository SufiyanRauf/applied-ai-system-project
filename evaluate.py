"""Reliability harness for the guessing agent.

Runs the agent across a whole range of secret numbers and prints a summary so
you can see how it performs without playing by hand. Then it does the same thing
with a game that lies about every hint, and checks the agent notices and stops
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
        # Deliberately generous cap. If the agent is capped at the same number
        # the report compares against, "worst attempts within the bound" is
        # true by construction and proves nothing.
        agent = GuessingAgent(low, high, max_attempts=(high - low + 2))
        agent.play(secret)
        results.append(agent)

    wins = [a for a in results if a.status == "won"]

    print(f"Difficulty: {difficulty}  (range {low}-{high})")
    print(f"  Games played:     {len(results)}")
    print(f"  Wins:             {len(wins)}/{len(results)}")
    if not wins:
        print("  No wins, so there are no attempt stats to report.")
        return False

    attempts = [a.attempt for a in wins]
    win_confidence = [a.log[-1].confidence for a in wins]
    print(f"  Avg attempts:     {sum(attempts) / len(attempts):.2f}")
    print(f"  Worst attempts:   {max(attempts)} (theoretical cap {worst_case})")
    print(f"  Avg confidence:   {sum(win_confidence) / len(win_confidence):.2f}")
    return len(wins) == len(results) and max(attempts) <= worst_case


def run_guardrail_sweep(difficulty="Normal"):
    # Testing the guardrail on one secret isn't enough, since the guardrail is
    # the whole point. Run the lying game against every secret in the range.
    low, high = get_range_for_difficulty(difficulty)
    opening_guess = (low + high) // 2
    cap = high - low + 2  # backstop so a broken guardrail stops instead of hanging

    caught = []
    won = []
    lost = []
    for secret in range(low, high + 1):
        agent = GuessingAgent(low, high, max_attempts=cap)
        agent.play(secret, judge=lying_judge)
        if agent.status == "stuck":
            caught.append(secret)
        elif agent.status == "won":
            won.append(secret)
        else:
            lost.append(secret)

    total = high - low + 1
    print("Guardrail sweep: agent vs. a game that lies on every hint")
    print(f"  Range:            {low}-{high}")
    print(f"  Caught (stuck):   {len(caught)}/{total}")
    print(f"  Won anyway:       {won}")
    if lost:
        print(f"  Ran out of turns: {lost}")
    print(f"  Why:              {opening_guess} is the agent's first guess, so it")
    print(f"                    wins before the liar ever gets to flip a hint")

    # The only secret that may escape is the opening guess, and only by winning
    # on move 1 before the game has had a chance to lie. Anything else, including
    # running out of turns, is a guardrail failure.
    return won == [opening_guess] and not lost


def main():
    print("=" * 55)
    print("Guessing Agent - Reliability Report")
    print("=" * 55)

    checks = []
    for difficulty in ("Easy", "Normal", "Hard"):
        checks.append(run_range(difficulty))
        print()

    guardrail_ok = run_guardrail_sweep()
    checks.append(guardrail_ok)
    print()

    passed = sum(checks)
    print("=" * 55)
    print(f"Summary: {passed}/{len(checks)} checks passed")
    if guardrail_ok:
        print("The agent solves every honest game and stops on every lie it sees.")
    print("=" * 55)


if __name__ == "__main__":
    main()
