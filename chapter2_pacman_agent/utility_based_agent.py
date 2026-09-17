"""Part 5 - Utility-based agent (AIMA 4e Figure 2.14).

This agent keeps everything Part 3 (model-based reflex) has -- internal
state built from the percept sequence, given to you below unchanged --
and replaces its condition-action RULES with a single UTILITY FUNCTION:
every legal action is scored on one numeric scale that blends several
competing preferences (closer food is good, closer danger is bad,
repetition is mildly bad, and so on), and the agent takes whichever
action scores highest. That is the qualitative jump from Part 4: a
goal-based agent asks "does this satisfy the goal, or get me closer to
it"; a utility-based agent asks "how good is this, all things considered"
and can trade one desideratum off against another inside a single number.

Do NOT implement your own search (BFS, DFS, A*, ...). ``self.maze.distance``
is provided precisely so you never have to.

TODO(CH2-5a), TODO(CH2-5b), TODO(CH2-5c) mark what to do. Delete each
marker once that piece is done.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "utility_based"


@dataclass(frozen=True)
class Percept:
    player: tuple[int, int]
    current_direction: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    released_ghosts: tuple[tuple[int, int], ...]
    legal_actions: tuple[tuple[int, int], ...]
    frightened_time_remaining: float

    @property
    def frightened(self) -> bool:
        return self.frightened_time_remaining > 0.0


# =====================================================================
# TODO(CH2-5a)  Named utility weights
# =====================================================================
# A utility function that hides its preferences inside bare numbers is
# unreadable. Every number that expresses a preference belongs here, with
# a name. At minimum you need weights covering:
#
#   catching a frightened ghost         a dangerous ghost one step away
#   closing distance on a frightened    a dangerous ghost two steps away
#     ghost (should be NEGATIVE: closer   a dangerous ghost three steps away
#     is more attractive)               keeping a comfortable distance
#   colliding with a dangerous ghost      beyond that, with a cap
#   continuing in the same direction    revisiting a tile (per visit)
#   reversing into the tile you just left
#
# food_distance, regular_pellet, and power_pellet are started for you.
# Pick your own numbers for the rest -- you will defend them in the
# write-up. A reader should be able to tell what this agent wants by
# reading this class alone.
# =====================================================================
@dataclass(frozen=True)
class UtilityWeights:
    """Named preferences. This is the agent's utility function, not the
    environment's performance measure (AIMA 4e Section 2.2 keeps those
    separate on purpose; so does this codebase -- see pacman/rules.py)."""

    food_distance: float = -2.0
    regular_pellet: float = 25.0
    power_pellet: float = 80.0
    # TODO(CH2-5a): add the remaining named weights here.
    ghost_catch_frightenend: float = 140.0 # reward for eating frightened ghost
    ghost_close_frightened: float = -4.0 # smaller distance = smaller penalty for being close to frightened ghost
    ghost_collision: float = -2600.0 # penalty for hitting a ghost that is not frightened
    # penalty for being too close to ghost
    ghost_one_step: float = -350.0
    ghost_two_step: float = -90.0
    ghost_three_step: float = -30.0
    ghost_safe_distance: float = 3.0 # reward for staying more than three steps away from ghost
    ghost_safe_distance_cap: float = 15.0 # max reward so no hiding
    continuation: float = 2.0 # prevent unnessacary turning
    revisit_per_visit: float = -4.0 # penalty for exploring same spot more than once
    backtrack: float = -10.0 # penalty for going back direction came from


class UtilityBasedAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.weights = UtilityWeights()
        self.last_reason = "Waiting for first percept."

        # Internal state, carried over unchanged from Part 3.
        self.visit_counts: dict[tuple[int, int], int] = {}
        self.position_history: deque[tuple[int, int]] = deque(maxlen=4)
        self.revisit_decisions = 0
        self.backtrack_decisions = 0

    def update_internal_state(self, percept: Percept) -> None:
        """Same as Part 3: record that percept.player has been visited
        and append it to position_history. Provided -- you already built
        this once."""
        position = percept.player
        self.visit_counts[position] = self.visit_counts.get(position, 0) + 1
        self.position_history.append(position)

    # -------------------------------------------------------------
    # TODO(CH2-5b)  Evaluate one action
    # -------------------------------------------------------------
    def evaluate_action(
        self,
        percept: Percept,
        action: tuple[int, int],
    ) -> tuple[float, dict[str, float]]:
        """Score a single legal action.

        Returns ``(total_utility, contributions)`` where ``contributions``
        maps a term name to the signed number it added. Splitting scoring
        out from choosing is what lets you explain a decision instead of
        just making one.

        ``contributions`` must contain at least these keys:

            food_distance   revisit          food_distance_steps
            regular_pellet  backtrack        ghost_distance_steps
            power_pellet    continuation     revisit_count
            ghost

        The first two columns are weighted values that sum into the
        total. The third column is raw evidence, not weighted, used for
        reporting.

        Behaviour to implement:
          - Raise ValueError if ``action`` is not in ``percept.legal_actions``.
          - Work out the landing tile with ``self.maze.step``.
          - Pull food and ghost distances from ``self.maze.distance``
            (pass an empty/absent ghost set as a very large number, e.g.
            10_000, so "no ghosts released" never reads as "ghost is
            here").
          - When frightened, closer ghosts should be more attractive
            (negative distance coefficient), and landing on one is worth
            a lot.
          - When not frightened, landing on a ghost is disastrous, and
            ghosts one, two, or three steps away are progressively less
            alarming. Beyond that, more space is mildly good; cap it so
            the agent does not just run to the far corner and idle.
          - Penalise the landing tile in proportion to
            ``self.visit_counts``.
          - Penalise the landing tile if it equals
            ``self.position_history[-2]`` (the tile from two turns ago;
            only meaningful once history has at least 2 entries).
        """
        if action not in percept.legal_actions:
            raise ValueError(f"Illegal action: {action}")

        w = self.weights
        landing = self.maze.step(percept.player, action)

        food = set(percept.pellets) | set(percept.power_pellets)
        ghosts = set(percept.released_ghosts)

        food_distance = self.maze.distance(landing, food)

        if  ghosts:
            ghost_distance = self.maze.distance(landing, ghosts)
        else:
            ghost_distance = 10000

        revisit_count = self.visit_counts.get(landing, 0)

        
        contributions = {} # keep track of action score

        contributions["food_distance"] = w.food_distance * food_distance

        if landing in percept.pellets:
            contributions["regular_pellet"] = w.regular_pellet
        else:
            contributions["regular_pellet"] = 0.0

        if landing in percept.power_pellets:
            contributions["power_pellet"] = w.power_pellet # if eats power pellet, + amoutn for power pellet
        else:
            contributions["power_pellet"] = 0.0 # else none

        contributions["ghost"] = 0.0
        contributions["revisit"] = w.revisit_per_visit * revisit_count
        contributions["backtrack"] = 0.0

        if action == percept.current_direction:
            contributions["continuation"] = w.continuation
        else:
            contributions["continuation"] = 0.0

        contributions["food_distance_steps"] = food_distance
        contributions["ghost_distance_steps"] = ghost_distance
        contributions["revisit_count"] = revisit_count


        if ghosts:
            if percept.frightened:
                contributions["ghost"] += w.ghost_close_frightened * ghost_distance

                if landing in ghosts:
                    contributions["ghost"] += w.ghost_catch_frightenend
            else:
                if ghost_distance == 0:
                    contributions["ghost"] += w.ghost_collision
                elif ghost_distance == 1:
                    contributions["ghost"] += w.ghost_one_step
                elif ghost_distance ==2 :
                    contributions["ghost"] += w.ghost_two_step
                elif ghost_distance ==3 :
                    contributions["ghost"] += w.ghost_three_step
                else:
                    safe_bonus = w.ghost_safe_distance * (ghost_distance -3)
                    contributions["ghost"] += min(safe_bonus, w.ghost_safe_distance_cap)


        if len(self.position_history) >= 2:
            previous_title = self.position_history[-2]

            if landing == previous_title:
                contributions["backtrack"] = w.backtrack

        weighted_term = (
            "food_distance",
            "regular_pellet",
            "power_pellet",
            "ghost",
            "revisit",
            "backtrack",
            "continuation"
        )

    # -------------------------------------------------------------
    # TODO(CH2-5c)  Select, and explain
    # -------------------------------------------------------------
    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Replace the starter policy below.

        Requirements:
          - If there are no legal actions, set ``last_reason`` to a string
            containing "No legal" and return ``(0, 0)``.
          - Otherwise call ``update_internal_state`` exactly once, score
            every legal action with ``evaluate_action``, and return the
            best one. Iterate in ``percept.legal_actions`` order and keep
            strictly-greater comparison so ties break the same way every
            time.
          - The returned action must always be legal.
          - Set ``self.last_reason`` to one short line containing the
            direction name and the tokens "U=", "food=", "ghost=", and
            "memory=", where memory is the sum of the revisit and
            backtrack contributions for the chosen action. Example:

                LEFT | U=-31.0 | food=3 | ghost=6 | memory=-2.0

            That line is drawn live in the game window -- the fastest way
            to debug a utility function is to watch a percept become a
            number and the number become a move.
        """
        # ---------------- starter policy, replace this ----------------
        # A simple reflex agent: it walks toward the nearest food and is
        # completely unaware of ghosts, of its own heading, and of
        # anywhere it has already been. This is here so the file runs
        # before you finish it -- it is not a model answer.
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        
        # -------------- end of starter policy to replace --------------
