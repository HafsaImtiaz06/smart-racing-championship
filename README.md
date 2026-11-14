# Smart Racing Championship (DAA)

## Setup
1. Python 3.10+  2. `pip install -r requirements.txt` (pygame-ce; matplotlib only for experiment charts)
3. Run tests: `python -m unittest discover tests`   4. Run game: `python main.py` (after GUI is integrated)

## Ownership (never edit another person's folder; ask or open a pull request)
| Folder | Owner |
|---|---|
| src/core (constants, models, graph, track_io, results) | FROZEN, change only by agreement of all three |
| src/routing | Person A |
| src/planning, src/events, src/generation | Person B |
| src/ranking, src/game | Person C |
| src/gui | per-file, see src/gui/README.md |
| tracks/circuit1.json / circuit2.json / circuit3.json | A / B / C |
| tests/test_<module>.py, experiments/expN_*.py | the module owner |

## Contract rule
Each `api.py` holds the agreed function signatures. Implement behind them. If a signature must change, tell the others first.
