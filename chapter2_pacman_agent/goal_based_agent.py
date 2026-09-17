"""Part 4 - Goal-based agent (AIMA 4e Figure 2.13).

The structural addition this part asks for is an explicit GOAL and a GOAL
TEST, not a graded preference over many factors (that is Part 5). This
agent maintains one goal at a time -- either "reach food" or "get away
from a ghost" -- and picks whichever legal action's resulting state gets
closest to satisfying it, using the same ``self.maze.distance`` oracle
every other part uses. There is no numeric weighing of competing desires
here: a state either satisfies the goal or it does not, and short of
that, closer is better and further is worse. Do not add a UtilityWeights
class or blend multiple scored terms into one number -- that is Part 5.

This agent does not need the memory from Part 3 to do its job -- the goal
is recomputed fresh from each percept -- so it is intentionally left out.

TODO(CH2-4a), TODO(CH2-4b), TODO(CH2-4c) mark what to do.
"""

from __future__ import annotations

from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "goal_based"


@dataclass(frozen=True)
class Percept:
    player: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    released_ghosts: tuple[tuple[int, int], ...]
    legal_actions: tuple[tuple[int, int], ...]
    frightened_time_remaining: float

    @property
    def frightened(self) -> bool:
        return self.frightened_time_remaining > 0.0


class GoalBasedAgent:
    percept_class = Percept

    #: How close a dangerous ghost has to be, in steps, before survival
    #: becomes the active goal instead of eating.
    DANGER_RADIUS = 3

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."

    # -------------------------------------------------------------
    # TODO(CH2-4a)  Pick the goal
    # -------------------------------------------------------------
    def determine_goal(self, percept: Percept) -> tuple[str, frozenset]:
        """Return ``(kind, positions)``.

        If there is a dangerous (non-frightened) released ghost within
        ``self.DANGER_RADIUS`` steps of the player (use
        ``self.maze.distance``), return ``("flee", <frozenset of the
        released ghost positions>)``.

        Otherwise return ``("seek", <frozenset of pellets and power
        pellets>)``. If frightened AND there are released ghosts, they
        count as food too -- add them to the seek set. If there is no
        food left at all, fall back to ``frozenset({percept.player})`` so
        the set is never empty.
        """
        # frozenset of the released ghost positions>
        ghosts = frozenset(percept.released_ghosts)

        if (
            not percept.frightened
            and ghosts
            and self.maze.distance(percept.player, ghosts) <= self.DANGER_RADIUS
        ) :
            return "flee", ghosts

        #<frozenset of pellets and power pellets>
        food = percept.pellets | percept.power_pellets

        if percept.frightened:
            food |= ghosts

        if not food:
            food = frozenset({percept.player})

        return "seek", food

    # -------------------------------------------------------------
    # TODO(CH2-4b)  Test the goal
    # -------------------------------------------------------------
    def goal_test(self, position: tuple[int, int], goal: tuple[str, frozenset]) -> bool:
        """Has ``position`` achieved ``goal``?

        For a "seek" goal: True iff position is one of the goal positions.
        For a "flee" goal: True iff position is MORE than
        self.DANGER_RADIUS steps (self.maze.distance) from every goal
        position.
        """
        goal_positions, the_goal = goal

        if goal_positions == "seek":
            return position in the_goal

        if goal_positions == "flee":
            return(self.maze.distance(position, the_goal) > self.DANGER_RADIUS)

        raise ValueError(f"Goal Unknown: {goal_positions}")
        
    
        

    # -------------------------------------------------------------
    # TODO(CH2-4c)  Act toward the goal
    # -------------------------------------------------------------
    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Requirements:
          - If there are no legal actions, set last_reason to a string
            containing "No legal" and return (0, 0).
          - Call self.determine_goal(percept) once.
          - For each legal action, find the landing tile
            (self.maze.step) and its distance to the goal positions
            (self.maze.distance). For a "seek" goal, smaller distance is
            better; for a "flee" goal, LARGER distance is better -- pick
            whichever legal action optimizes that, iterating in
            percept.legal_actions order and comparing with strict
            inequality so ties break the same way every time.
          - Set self.last_reason to a short line naming the direction,
            the goal kind, whether goal_test passed on the chosen
            landing tile, and the distance, e.g.:
            "RIGHT | goal=seek | achieved=False | dist=4"
        """
        if not percept.legal_actions:
            self.last_reason = "No legal actions"
            return (0, 0)

        goal = self.determine_goal(percept)
        goal_positions, the_goal = goal

        optimal_action = None
        optimal_start = None
        optimal_distance = None

        for legal_action in percept.legal_actions:
            start = self.maze.step(percept.player, legal_action)
            distance = self.maze.distance(start, the_goal)

            if optimal_distance is None:
                optimal_action = legal_action
                optimal_start = start
                optimal_distance = distance
            elif goal_positions == "seek" and distance < optimal_distance:
                optimal_action = legal_action
                optimal_start = start
                optimal_distance = distance
            elif goal_positions == "flee" and distance > optimal_distance:
                optimal_action = legal_action
                optimal_start = start
                optimal_distance = distance 

        achieved = self.goal_test(optimal_start, goal)
        direction = DIRECTION_NAMES[optimal_action]        

        self.last_reason = (
            f"{direction} | goal={goal_positions} | achieved={achieved} | dist={optimal_distance}"
        )
        return optimal_action
