# Challenge 2 - Multi-objective route planning (draft sheet, auto-generated)

Circuit: Circuit 1 - Coastal Loop. Lap = Start -> checkpoints 1..10 in order -> Finish. Date: 2026-11-20 15:40 | Python 3.13.15 (CPython) | OS: Windows-11-10.0.26300-SP0 | CPU: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, AMD64, 8 logical cores

## 1. What each preset chooses (whole lap)
| preset | roads | distance | time s | fuel | cost (own preset) |
|---|---|---|---|---|---|
| Balanced | 17 | 2626.6 | 75.5 | 152.7 | 5.1115 |
| Speed | 17 | 2654.7 | 57.5 | 172.5 | 4.0144 |
| Economy | 17 | 2626.6 | 75.5 | 152.7 | 5.9596 |
| Safety | 23 | 3968.2 | 146.5 | 166.9 | 3.3261 |

3 distinct routes among the 4 presets.

## 2. Cost of each preset's route under every preset's weights (percent above the best route for that column)
| route chosen by \ cost under | Balanced | Speed | Economy | Safety |
|---|---|---|---|---|
| Balanced | 5.112 (+0.0%) | 4.289 (+6.8%) | 5.960 (+0.0%) | 3.660 (+10.0%) |
| Speed | 5.319 (+4.1%) | 4.014 (+0.0%) | 6.465 (+8.5%) | 4.168 (+25.3%) |
| Economy | 5.112 (+0.0%) | 4.289 (+6.8%) | 5.960 (+0.0%) | 3.660 (+10.0%) |
| Safety | 6.615 (+29.4%) | 6.571 (+63.7%) | 7.100 (+19.1%) | 3.326 (+0.0%) |

## 3. Weight sweep: time weight from 0 to 1, other weights scaled to keep the sum at 1
Chosen routes in order: route A, route B, route C, route D. Switch points: route B at w_t = 0.10; route C at w_t = 0.35; route D at w_t = 0.45.
| w_t | route | distance | time s | fuel |
|---|---|---|---|---|
| 0.0 | route A | 2809.0 | 88.0 | 149.6 |
| 0.05 | route A | 2809.0 | 88.0 | 149.6 |
| 0.1 | route B | 2626.6 | 75.5 | 152.7 |
| 0.15 | route B | 2626.6 | 75.5 | 152.7 |
| 0.2 | route B | 2626.6 | 75.5 | 152.7 |
| 0.25 | route B | 2626.6 | 75.5 | 152.7 |
| 0.3 | route B | 2626.6 | 75.5 | 152.7 |
| 0.35 | route C | 2626.0 | 66.8 | 160.6 |
| 0.4 | route C | 2626.0 | 66.8 | 160.6 |
| 0.45 | route D | 2654.7 | 57.5 | 172.5 |
| 0.5 | route D | 2654.7 | 57.5 | 172.5 |
| 0.55 | route D | 2654.7 | 57.5 | 172.5 |
| 0.6 | route D | 2654.7 | 57.5 | 172.5 |
| 0.65 | route D | 2654.7 | 57.5 | 172.5 |
| 0.7 | route D | 2654.7 | 57.5 | 172.5 |
| 0.75 | route D | 2654.7 | 57.5 | 172.5 |
| 0.8 | route D | 2654.7 | 57.5 | 172.5 |
| 0.85 | route D | 2654.7 | 57.5 | 172.5 |
| 0.9 | route D | 2654.7 | 57.5 | 172.5 |
| 0.95 | route D | 2654.7 | 57.5 | 172.5 |
| 1.0 | route D | 2654.7 | 57.5 | 172.5 |
Chart: challenge2_weights.png

## 4. Pareto analysis of one leg (all simple routes up to 12 roads)
| quantity | value |
|---|---|
| leg | 2 -> 4 |
| simple routes enumerated (complete, max 12 roads) | 201 |
| Pareto-optimal routes (5 objectives) | 3 |
| Pareto routes chosen by some sampled weights | 2 |
| Pareto routes never chosen by any sampled weights | 1 |
| distinct routes chosen by the 4 presets | 2 |
Sampling many random weight vectors cannot prove that a Pareto route is unreachable, but a route that is never chosen after thousands of samples is a strong sign of an unsupported (non-convex) trade-off.

## 5. Sensitivity to the normalization constant T_ref (Balanced preset)
| T_ref x | roads | distance | time s | fuel | route |
|---|---|---|---|---|---|
| 0.25 | 17 | 2654.7 | 57.5 | 172.5 | route A |
| 0.5 | 17 | 2626.0 | 66.8 | 160.6 | route B |
| 1.0 | 17 | 2626.6 | 75.5 | 152.7 | route C |
| 2.0 | 17 | 2626.6 | 75.5 | 152.7 | route C |
| 4.0 | 17 | 2626.6 | 75.5 | 152.7 | route C |

## Discussion points to write yourself from these tables
- Why one scalar cost hides trade-offs (a route can be cheap overall yet bad on one objective; section 2 shows the regret).
- Why the weights and the normalization constants are arbitrary choices that change the answer (sections 3 and 5).
- Why weighted sums cannot reach every Pareto-optimal route (section 4), and what a Pareto-front presentation would add.
- How the game uses the presets: the player picks the trade-off; the planner optimizes exactly the scalar cost it displays.
