# Circuit JSON format
{ "name": "...", "vertices": [ {id, x, y, type, checkpointOrder|null, active} ],
  "edges": [ {id, from, to, distance, baseTime, fuelCost, difficulty 1-5, status, isShortcut, directed} ],
  "main_route": [vertex ids]           (optional, Opponent 1 fixed route),
  "fixed_detour": {"<edge id>": [vertex ids]}   (optional, Opponent 1 detours),
  "events": [ {type, time, target, duration|null} ]   (optional scripted race events) }
Rules: distance >= straight-line distance between endpoints (A* admissibility). Vertex 0 = Start. One Finish.
Circuits: circuit1.json (Person A), circuit2.json (Person B), circuit3.json (Person C). Each: >=10 checkpoints, >=2 shortcuts, a cycle, a dead end.

## Extra keys used by circuit1.json (ignored by core/track_io.py; read them with json.load)
- "lap_boundary": id of the Finish vertex. A lap counts when the racer crosses it after checkpoints 1..10 in order.
  Racers start at Start; later laps run Finish -> Start -> checkpoint 1.
- "main_route": Opponent 1's fixed route for one lap (Start, CP1..CP10, Finish); repeat for later laps.
- "fixed_detour": {"<edge id>": [vertex ids]} the documented detour that replaces that road when it is blocked.
- Vertices also carry a "name" (for the GUI). Canvas is about 1040 x 680 units.
