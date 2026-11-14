"""FROZEN SHARED CONSTANTS (Step 0). Change only if all 3 members agree.
Spec reference: Sections 3.3, 4.2-4.6. Units: distance = map units, time = seconds, fuel = fuel units."""

# ---- Race rules (4.2) ----
LAPS = 2
TIME_LIMIT = 900.0            # seconds; racers unfinished at limit get NO points (documented rule)
RECOVERY_MAX_WAIT = 60.0      # blocked with no route: reroute -> else wait up to this long -> else DNF (same for all racers)

# ---- Fuel and nitro (4.3) ----
MAX_FUEL = 100.0
FUEL_SCALE = 10               # DP unit = 0.1 fuel (tenths). Tank = 1000 DP units.
STATION_MAX_BUY = 40.0
STATION_STOP_TIME = 5.0       # fixed seconds for any positive purchase
MAX_NITRO = 3
START_NITRO = 1
NITRO_SPEED_FACTOR = 1.5
NITRO_DURATION = 4.0
NITRO_FUEL_FACTOR = 2.0

def difficulty_multiplier(difficulty: int) -> float:
    return 1.0 + 0.1 * (difficulty - 1)

# ---- Opponents (4.4) ----
HUMAN_ID = 0
OPPONENT_IDS = (1, 2, 3)
REFUEL_THRESHOLD = 0.25       # refuel below 25% fuel

# ---- Events (4.5): priority number (lower fires first) and default duration (None = until reversed/cleared) ----
EVENT_PRIORITY = {"ROAD_BLOCKAGE": 1, "SHORTCUT_TOGGLE": 2, "OIL_SPILL": 3,
                  "SPEED_RESTRICTION": 4, "STATION_AVAILABILITY": 5, "NITRO_BOOSTER": 6}
EVENT_DURATION = {"ROAD_BLOCKAGE": None, "SHORTCUT_TOGGLE": None, "OIL_SPILL": 20.0,
                  "SPEED_RESTRICTION": 15.0, "STATION_AVAILABILITY": 30.0, "NITRO_BOOSTER": 25.0}
OIL_DIFFICULTY_ADD = 2        # oil spill: effective difficulty = min(5, base + 2), obstacle penalty 1
OIL_SPEED_FACTOR = 0.8
SPEED_RESTRICTION_FACTOR = 0.6
RESTRICTED_TIME_FACTOR = 1.5  # Restricted edge: traversable, time x1.5, obstacle penalty 0.5
RESTRICTED_OBSTACLE = 0.5

# ---- Scoring (4.6) ----
POINTS_TABLE = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]   # positions 1..10
FASTEST_LAP_BONUS = 1         # bonus: best fastest lap among FINISHERS in that race (defined before testing)

# ---- Cost presets (3.3): weights (w_d, w_t, w_f, w_r, w_o), each preset sums to 1.0 ----
PRESETS = {
    "Balanced": (0.25, 0.25, 0.25, 0.15, 0.10),
    "Speed":    (0.15, 0.55, 0.10, 0.10, 0.10),
    "Economy":  (0.15, 0.15, 0.55, 0.10, 0.05),
    "Safety":   (0.10, 0.10, 0.10, 0.40, 0.30),
}
DEFAULT_PRESET = "Balanced"
