# AI Interactions Log

Notes on the stretch features I attempted. The agent's own reasoning traces are
embedded below so they can be read without running anything.

---

## Agent Workflow (SF8)

**What task did you give the agent?**

Solve the guessing game on its own for any secret number in the range, and stop
safely if the game's hints can't be trusted.

**What did the agent do?**

It runs a plan / act / observe / revise / check loop (`GuessingAgent.step` in
`agent.py`). Each turn it picks the midpoint of the range it still thinks is
possible, submits it to `check_guess`, reads the hint, narrows the range, and
then checks that the narrowed range is still possible. Here is a full reasoning
trace for a normal round where the secret is 63:

```
secret = 63, range 1-100
  attempt 1: guessed  50 -> Too Low   range now 51-100 confidence 0.51
  attempt 2: guessed  75 -> Too High  range now 51-74  confidence 0.77
  attempt 3: guessed  62 -> Too Low   range now 63-74  confidence 0.89
  attempt 4: guessed  68 -> Too High  range now 63-67  confidence 0.96
  attempt 5: guessed  65 -> Too High  range now 63-64  confidence 0.99
  attempt 6: guessed  63 -> Win       range now 63-64  confidence 1.0
status: won
```

And here is the trace when the game lies about every hint. The agent gets pushed
the wrong way until its range collapses, then it stops instead of looping:

```
lying game, secret = 42
  attempt 1: guessed  50 -> Too Low   range now 51-100
  attempt 2: guessed  75 -> Too Low   range now 76-100
  attempt 3: guessed  88 -> Too Low   range now 89-100
  attempt 4: guessed  94 -> Too Low   range now 95-100
  attempt 5: guessed  97 -> Too Low   range now 98-100
  attempt 6: guessed  99 -> Too Low   range now 100-100
  attempt 7: guessed 100 -> Too Low   range now 101-100  hints contradict each other, stopping
status: stuck
```

**What did you have to verify or fix manually?**

I checked that the range in each step actually matched the hint (a Too High should
lower the top of the range, a Too Low should raise the bottom), and I confirmed
the confidence numbers made sense as the range shrank. I also had to fix the
confidence formula: the first version reported a misleading probability, so I
changed it to the fraction of the range ruled out. Details are in
[model_card.md](model_card.md).

---

## Test Generation (SF7)

I asked Claude to help write tests that target specific behaviors, then ran each
one myself with pytest.

| Edge case | Prompt used | AI-suggested test | Did it pass? | My reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Agent wins every possible game | "Write a test that the agent solves every secret in 1-100" | `test_agent_wins_every_normal_game` loops all secrets and asserts "won" | Yes | I wanted proof it works for the whole range, not one lucky number I happened to pick |
| Agent stays within the math bound | "Check it never uses more guesses than binary search should" | `test_agent_stays_within_binary_search_bound` compares attempts to `floor(log2(range))+1` | Yes | Winning slowly would still be a bug, so efficiency needed its own check |
| Lying game is caught | "Test that a game flipping its hints makes the agent stop" | `test_guardrail_detects_lying_game` uses `lying_judge` and asserts "stuck" | Yes | The guardrail is the main point of the project, so I didn't want to trust it without a test |

---

## Test Harness (SF10)

`evaluate.py` is the evaluation script. It runs the agent on every secret number
across all three difficulties (320 games total), prints win rate, average
attempts, worst case, and average confidence, and then stress-tests the guardrail
against a lying game. Full output is pasted in the README under "Reproducible
execution evidence."
