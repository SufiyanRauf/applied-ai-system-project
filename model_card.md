# Model Card: Guessing Game Agent

This project doesn't use a trained model. The "model" here is a rule-based agent
that solves the guessing game with binary search. I'm still filling out a model
card for it because the same questions about limits, misuse, and reliability
apply to any system that makes decisions on its own.

## What the system does

`GuessingAgent` plays the number-guessing game. It plans a guess, submits it,
reads the hint, narrows its range, and then checks that the narrowed range still
describes a possible number. It stops in one of four ways: it wins, it decides
the hints contradict each other, it gets an answer it can't read at all, or it
runs out of attempts. The attempt cap is always set, so there is no way to build
one that runs forever. It reports a step log and a confidence score.

## Limitations and biases

- **It only solves this one problem.** The agent assumes the answer is a single
  integer in a known range and that hints are ordered (higher/lower). It can't do
  anything outside that. There's no general reasoning here.
- **It trusts the range it's told.** If the secret number is actually outside the
  low-to-high range the app passes in, the agent's search will collapse and it
  will report "stuck," the same way it does for a lying game. It can't tell those
  two situations apart.
- **The confidence score is not a probability.** It's just the fraction of the
  range that has been ruled out. It says how much progress the agent has made, not
  how likely the next guess is to be right. I kept it simple on purpose so it
  wouldn't look more sophisticated than it is. Two exceptions worth naming, since
  the point of this number is being honest about what it measures: a win is
  reported as exactly 1.0 rather than computed, and a contradiction reports 0.0,
  because "fraction of the range ruled out" has no honest answer once the range is
  empty. Without that second rule the formula ran past 1.0 when the bounds crossed,
  and a stuck row looked identical to a winning one.
- **Bias in the usual sense doesn't really apply** because there's no training
  data and no people involved. The closest thing to a bias is that binary search
  always guesses the midpoint, so its behavior is completely predictable and never
  adapts to anything about who is playing.

## What I would improve next

- **Tell a lying game apart from a bad range.** Right now both collapse the range
  and both report "stuck," and the agent can't say which happened. I'd give it a
  way to test a bound directly instead of only guessing midpoints, so it could
  check whether the answer is even inside the range it was handed.
- **Catch a game that lies only sometimes.** The consistency check fires when the
  bounds cross, so it does catch an occasional liar, but it gets worse the later
  the lie lands. A single lie on the first turn is caught in 99 of 100 games, on
  the third turn 93, and on the sixth only 37, because a late lie has fewer turns
  left to push a bound off the end of the range. A judge that answers honestly
  about a *different* number never crosses the bounds at all, so the agent reports
  a confident win on the wrong answer. The fix for both is to re-check every hint
  it has seen against its current range rather than only checking that the range
  is non-empty.
- **Move the range check into shared logic.** The app now turns away a guess
  outside the current range, and `parse_guess` stays format-only on purpose, with
  a test that pins it letting `999999` through. The gap left is that the range
  check lives in `app.py`, so anything that called `parse_guess` without going
  through the app would still accept an out-of-range number. I'd put that check
  somewhere the app and any other caller both share.

## Could it be misused, and how would I prevent that?

On its own this is a harmless toy, so the honest answer is that the game itself is
low risk. The pattern behind it is the part worth being careful with: an agent
that acts in a loop and reports high confidence. If someone reused this loop for a
task where being wrong actually costs something, the danger is that a confident
looking score gets trusted without anyone checking the work.

The main guard I built for that is the consistency check. The agent refuses to
keep going when the feedback it's getting can't all be true, instead of pushing
ahead and pretending it's fine. I'd keep that habit in any reuse: give the agent a
clear way to say "I can't trust this input, stopping," cap the number of steps so
it can't run away, and keep the step log so a person can see exactly what it did.
For this project the human review step is the harness and pytest, which I run and
read before trusting a change.

## What surprised me while testing reliability

The thing that surprised me was how badly the agent fails without the guardrail.
Before I added the consistency check, I ran it against the lying game and it just
kept guessing 100 over and over, fully "confident," never stopping. It looked
busy and sure of itself while being completely stuck. That made the point of the
whole project concrete for me: the agent is only as reliable as the feedback it
gets, and a system that can't recognize bad input will happily keep working on
garbage. Adding the bound-crossing check turned an infinite loop into a clean
"stuck" status.

The other small surprise was the worst-case attempt counts lining up exactly with
the binary-search math (7 for a range of 100, 8 for 200). Seeing the harness
confirm the theory across all 320 games was satisfying.

## Collaboration with AI

I built this with Claude. I described the game and the agent idea, reviewed the
code it wrote, and ran everything myself before keeping it.

**One helpful suggestion.** When I was thinking about the guardrail, I wasn't sure
how the agent should detect a dishonest game. Claude pointed out that if the hints
are honest, the low bound can never pass the high bound, so a crossed bound is
proof the hints contradict each other. That turned out to be a clean, exact test
with no guessing involved, and it tied the guardrail directly back to the
backwards-hint bug from my Module 1 project. I verified it by writing the lying
judge in `evaluate.py` and confirming the agent lands on "stuck," which it does.

**One flawed suggestion.** For the confidence score, Claude first suggested using
`1 / number_of_candidates`, framed as the probability the current guess is
correct. It sounded reasonable, but when I traced it the numbers were misleading:
early on it reported very low confidence even though binary search was guaranteed
to win, and it made confidence look like a real probability estimate when it
wasn't. I dropped it and used the fraction of the range ruled out instead, which
is honest about what it actually measures. This was a good reminder that AI
suggestions can sound right and still describe the system in a way that isn't
true, so I need to check what a number actually means before shipping it.
