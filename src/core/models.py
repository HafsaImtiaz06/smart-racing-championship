"""FROZEN data model (spec Section 3). Field names follow the spec."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VertexType(str, Enum):
    START = "Start"; FINISH = "Finish"; CHECKPOINT = "Checkpoint"
    INTERSECTION = "Intersection"; FUEL_STATION = "FuelStation"
    NITRO_PICKUP = "NitroPickup"; DEAD_END = "DeadEnd"


class EdgeStatus(str, Enum):
    OPEN = "Open"; BLOCKED = "Blocked"; RESTRICTED = "Restricted"


class EventType(str, Enum):
    ROAD_BLOCKAGE = "ROAD_BLOCKAGE"; SHORTCUT_TOGGLE = "SHORTCUT_TOGGLE"
    OIL_SPILL = "OIL_SPILL"; SPEED_RESTRICTION = "SPEED_RESTRICTION"
    STATION_AVAILABILITY = "STATION_AVAILABILITY"; NITRO_BOOSTER = "NITRO_BOOSTER"


@dataclass
class Vertex:
    id: int
    x: float
    y: float
    type: VertexType
    checkpointOrder: Optional[int] = None   # 1..10 for mandatory checkpoints, else None
    active: bool = True                     # for FuelStation / NitroPickup availability


@dataclass
class Edge:
    id: int
    from_: int          # JSON key "from"
    to: int
    distance: float
    baseTime: float
    fuelCost: float
    difficulty: int = 1              # 1..5
    status: EdgeStatus = EdgeStatus.OPEN
    isShortcut: bool = False
    directed: bool = False


@dataclass
class Effect:
    """A temporary effect on an edge. Each effect is stored independently with its own id."""
    effect_id: int
    kind: str       # "oil" (value = difficulty added) or "speed_cap" (value = speed factor 0..1)
    value: float


@dataclass
class Racer:
    id: int
    name: str
    isHuman: bool
    strategyType: str            # "human" | "fixed_route" | "shortcut_first" | "min_distance"
    currentVertex: int = 0
    fuel: float = 100.0
    nitroCharges: int = 1
    lap: int = 1
    nextCheckpoint: int = 1
    totalTime: float = 0.0
    finished: bool = False
    dnf: bool = False


@dataclass
class RaceResult:
    raceId: int
    racerId: int
    finishPosition: int
    finishTime: float
    fastestLap: float
    bonusPoints: int = 0
    pointsAwarded: int = 0


@dataclass
class ChampionshipEntry:
    racerId: int
    totalPoints: int = 0
    wins: int = 0
    sumOfFinishPositions: int = 0
    bestFastestLap: float = float("inf")


@dataclass
class Event:
    eventId: int
    type: EventType
    triggerTime: float
    priority: int
    insertionSequence: int
    targetEdgeOrVertex: int
    duration: Optional[float] = None
    cancelled: bool = False

    def key(self):
        """Heap key (spec 4.5): lower fires first."""
        return (self.triggerTime, self.priority, self.insertionSequence)


@dataclass
class RaceState:
    """Read-only snapshot passed by the race engine (Person C) to GUI overlays (Person B / C)."""
    graph: object
    racers: list = field(default_factory=list)
    time: float = 0.0
    event_log: list = field(default_factory=list)   # list[str], newest last
