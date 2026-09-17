# Chapter 2 Write-Up

Name: Isac Zarate, Karen Ocampo, Jonathon Chang
Date: 9/16/26

Keep this to three or four pages. Answer from the code in front of you,
not from the textbook in general. A correct answer that could have been
written without ever opening this project will not get full marks.

---

## 1. PEAS description (5 points)

Describe this task environment using AIMA Section 2.3.1. This is one
description for the whole environment -- all six of your agents share it.

**Performance measure.**
> What is the agent actually judged on? Name the function and the file.
> List every term in it, including the ones that cost points.

The agent is actually being judged on the performance() function in pacman/rules.py. regular pellets are +10, power pellets are +50, firghtened ghosts are +200, a win is +2000, caught is -1000, every decision is -.2, and a backtrack is -2.

**Environment.**
> The maze, the ghosts, the pellets, the clock. Mention anything that
> changes while an agent is deciding.

Things that change while an agent is deciding are pacman's location, ghost location, remaining pellets, and fightened mode

**Actuators.**
> What can an agent actually do? Be precise about how many actions it
> takes per turn and what happens if it picks an illegal one.

The agent can actually perform one movement each turn. If it picks an illegal one, pacman stays in the same place and the choice impacts the performance decision cost.

**Sensors.**
> What can an agent perceive? Name the mechanism that decides this, not
> just the list of possible fields -- and say why different parts of this
> project declare different subsets of them.

The mechanism that decides this is teh simulation.sense(). The different parts of this project declare different subset of them because each part represents a different type of agent and implementation.

---

## 2. Environment properties (6 points)

One row per dimension from AIMA Figure 2.6. Justify each from something
specific in the code, and name it.

| Property | This environment is... | Why (cite the code) |
|---|---|---|
| Fully or partially observable | partially obersvable|because simulation.sense() only provideds declared fields by the agent's percepts |
| Single-agent or multi-agent | multi-agent| pacman shares the environment with several ghosts|
| Deterministic or nondeterministic | nondeterministic| ghosts chase pacman but sometimes select random valid action, therfore pacman cannto know next ghost movement from current percept|
| Episodic or sequential | sequential| A decision changes pacman's position, remaining pellets, visit coutns, frightened mode, and the situation for future decisions|
| Static or dynamic |static but changed between turns | simulation does not move on to another event until choose_action() and _step_player return|
| Discrete or continuous |discrete | pac mand and the ghosts occupy the whole maze and the actions available are in discrete directions|
| Known or unknown |known |the agent is made with the static wall layout, legal connectivity, etc. |

**Follow-up.** Two of these have an argument on both sides in this
particular implementation. Pick one, and make the case for the answer you
did *not* put in the table.

The environment is static but there is a reasonable argument that it is dynamic since the "world" changes as the simulation goes on that are independently of the pacman action. Ghosts also have their own movement and characteristics. The reason for not putting dynamic is that the AIMA focuses on whether the environment changes while the agent is deliberating.

---

## 3. Six agents, six figures (6 points)

One row per part. Name the AIMA Section 2.4 figure it matches, and the
ONE concrete thing that part adds over the part before it (not a
restatement of what it does overall -- the specific delta).

| Part | Figure | What it adds over the previous part |
|---|---|---|
| 1. Table-driven | figure 2.7| (nothing to compare against -- say instead what makes it infeasible) |
| 2. Simple reflex | | |
| 3. Model-based reflex | | |
| 4. Goal-based | | |
| 5. Utility-based | | |
| 6. Learning | | |

**Two follow-ups:**

> For Part 2/3: you had a choice between `ghosts` and `released_ghosts`
> in your percepts. Say which you took and what the other one would have
> cost you.

> For Part 6: map the four boxes of AIMA Figure 2.15 (performance
> element, critic, learning element, problem generator) onto specific
> names in `learning_agent.py`.

---

## 4. Performance measure vs. utility function (5 points)

These are two different things, and this codebase keeps them in two
different places on purpose -- one in `pacman/rules.py`, imposed by the
environment designer, and one inside `utility_based_agent.py`, chosen by
you.

**Where does each one live?**
> File and function/class for both.

**Name one place they disagree.**
> Find something your utility function rewards (or punishes) that the
> performance measure does not, or the reverse. Explain why that gap
> exists and whether it is a flaw.

**Why does AIMA insist on the distinction?**
> Answer in your own words, in three or four sentences.

---

## 5. Rational is not the same as successful (4 points)

Run some `hard` trials with your Part 5 (or Part 6) agent and find a seed
where it lost.

**Seed:**

**What happened.**
> Replay it with `python tools/play.py --difficulty hard --agent
> utility_based --seed N` and describe the sequence.

**Why the losing decision was still rational.**
> AIMA Section 2.2.2 separates rationality from omniscience. Use it. What
> did the agent not know, and could it have known it given the percept it
> was handed and the "no search" rule every part in this project follows?

**What would have to change for that decision to be irrational?**

---

## 6. Trial results across all six parts (4 points)

Paste the summary table from `results/summary.csv` (both difficulties),
and a row for the trained `learning` agent from
`results/learned_weights.json`.

| agent | difficulty | trials | win_rate | caught_rate | mean_score | mean_decisions | mean_performance |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Interpretation, five to eight sentences.**
> Do not restate the numbers. Trace the progression: what does each part
> buy over the one before it, in terms of the agent structures involved
> rather than raw numbers? `mean_decisions` and `mean_backtracks` are the
> interesting columns for Parts 2 vs. 3 (memory); win rate and mean
> performance are the interesting columns for Parts 4 vs. 5 (goals vs.
> utility); the before/after numbers in `learned_weights.json` are the
> interesting ones for Part 6. If any part did NOT improve on the one
> before it in your results, say so and explain why -- that is a real
> finding, not something to hide.

---

## Optional

Anything you tried that did not work, or a weight you tuned and then
reverted. Not graded, but useful to me.
