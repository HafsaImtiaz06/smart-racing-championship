# Circuit JSON format
{ "name": "...", "vertices": [ {id, x, y, type, checkpointOrder|null, active} ],
  "edges": [ {id, from, to, distance, baseTime, fuelCost, difficulty 1-5, status, isShortcut, directed} ],
  "main_route": [vertex ids]           (optional, Opponent 1 fixed route),
  "fixed_detour": {"<edge id>": [vertex ids]}   (optional, Opponent 1 detours),
  "events": [ {type, time, target, duration|null} ]   (optional scripted race events) }
Rules: distance >= straight-line distance between endpoints (A* admissibility). Vertex 0 = Start. One Finish.
Circuits: circuit1.json (Person A), circuit2.json (Person B), circuit3.json (Person C). Each: >=10 checkpoints, >=2 shortcuts, a cycle, a dead end.
