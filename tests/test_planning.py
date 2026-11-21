import os, random, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.planning.api import knapsack_dp, greedy_select, refuel_plan, knapsack_bruteforce, recommend_pickups
from src.core import constants as K


class KnapsackTests(unittest.TestCase):
    def test_supplied_example_greedy_worse(self):
        c, v = [6, 5, 5], [30, 24, 24]
        d, g = knapsack_dp(c, v, 10), greedy_select(c, v, 10)
        self.assertEqual((d.best_value, d.chosen_ids), (48, [1, 2]))
        self.assertEqual((g.best_value, g.chosen_ids), (30, [0]))

    def test_team_cases_greedy_strictly_worse(self):
        for c, v, b in (([3, 2, 2], [9, 6, 6], 4), ([10, 6, 6, 1], [60, 35, 35, 1], 12)):
            self.assertGreater(knapsack_dp(c, v, b).best_value, greedy_select(c, v, b).best_value)

    def test_dp_matches_bruteforce_random(self):
        r = random.Random(1)
        for _ in range(300):
            m = r.randint(0, 10)
            c = [r.randint(0, 9) for _ in range(m)]
            v = [r.randint(0, 20) for _ in range(m)]
            b = r.randint(0, 25)
            res = knapsack_dp(c, v, b)
            self.assertEqual(res.best_value, knapsack_bruteforce(c, v, b))
            self.assertLessEqual(res.total_cost, b)
            self.assertEqual(sum(v[i] for i in res.chosen_ids), res.best_value)
            gr = greedy_select(c, v, b)
            self.assertLessEqual(gr.total_cost, b)
            self.assertLessEqual(gr.best_value, res.best_value)

    def test_zero_cost_and_empty(self):
        self.assertEqual(greedy_select([0, 0, 4], [5, 0, 9], 3).chosen_ids, [0])   # zero-cost zero-benefit skipped
        self.assertEqual(knapsack_dp([0], [7], 0).chosen_ids, [0])
        self.assertEqual(knapsack_dp([], [], 5).best_value, 0)
        self.assertEqual(knapsack_dp([3], [4], 0).chosen_ids, [])

    def test_equal_ratio_tie_lower_index(self):
        self.assertEqual(greedy_select([5, 5], [24, 24], 5).chosen_ids, [0])

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            knapsack_dp([1], [1, 2], 3)


class RefuelTests(unittest.TestCase):
    def test_full_tank_no_stop_needed(self):
        p = refuel_plan([30, 30], [True, True], 100, 100)
        self.assertTrue(p.feasible)
        self.assertEqual((p.extra_time, p.purchases), (0.0, [0.0, 0.0]))

    def test_needs_one_stop(self):
        p = refuel_plan([70, 70], [False, True], 100, 100)
        self.assertTrue(p.feasible)
        self.assertEqual(p.purchases[0], 0.0)
        self.assertGreaterEqual(100 - 70 + p.purchases[1], 70)
        self.assertEqual(p.extra_time, K.STATION_STOP_TIME)

    def test_capacity_and_max_buy_respected(self):
        p = refuel_plan([60, 60, 60], [True, True, True], 100, 100)
        self.assertTrue(p.feasible)
        fuel = 100
        for need, buy in zip([60, 60, 60], p.purchases):
            self.assertLessEqual(buy, K.STATION_MAX_BUY + 1e-9)
            fuel += buy
            self.assertLessEqual(fuel, 100 + 1e-9)
            fuel -= need
            self.assertGreaterEqual(fuel, -1e-9)

    def test_unavailable_station_infeasible(self):
        self.assertFalse(refuel_plan([70, 70], [False, False], 100, 100).feasible)

    def test_single_edge_longer_than_tank(self):
        self.assertFalse(refuel_plan([150], [True], 100, 100).feasible)

    def test_fractional_need_rounds_up(self):
        self.assertFalse(refuel_plan([100.04], [False], 100, 100).feasible)

    def test_matches_bruteforce_small(self):
        r = random.Random(3)
        for _ in range(40):
            need = [r.randint(5, 60) for _ in range(3)]
            st = [r.random() < 0.7 for _ in range(3)]
            p = refuel_plan(need, st, 100, 60)
            best = self._brute(need, st, 100, 60)
            self.assertEqual(p.feasible, best is not None)
            if best is not None:
                self.assertAlmostEqual(p.extra_time, best)

    @staticmethod
    def _brute(need, st, cap, f0):
        best = [None]

        def go(j, f, t):
            if j == len(need):
                best[0] = t if best[0] is None else min(best[0], t)
                return
            amts = [0] + (list(range(1, int(min(cap - f, K.STATION_MAX_BUY)) + 1)) if st[j] else [])
            for a in amts:
                if f + a >= need[j]:
                    go(j + 1, f + a - need[j], t + (K.STATION_STOP_TIME if a else 0))
        go(0, f0, 0.0)
        return best[0]


def _spur_graph(back_fuel, directed_back=True, out_fuel=5.0, with_return=True):
    """Route 0(Start) - 1(CP1) - 2(Finish), each leg 10 fuel. Nitro pickup 3 hangs off vertex 1 by a one-way spur."""
    from src.core.graph import Graph
    from src.core.models import Vertex, Edge, VertexType as VT, EdgeStatus
    g = Graph("spur")
    g.add_vertex(Vertex(0, 0, 0, VT.START, None))
    g.add_vertex(Vertex(1, 100, 0, VT.CHECKPOINT, 1))
    g.add_vertex(Vertex(2, 200, 0, VT.FINISH, None))
    g.add_vertex(Vertex(3, 100, 50, VT.NITRO_PICKUP, None))
    g.add_edge(Edge(0, 0, 1, 100, 3, 10.0, 1, EdgeStatus.OPEN, False, False))
    g.add_edge(Edge(1, 1, 2, 100, 3, 10.0, 1, EdgeStatus.OPEN, False, False))
    g.add_edge(Edge(2, 1, 3, 50, 2, out_fuel, 1, EdgeStatus.OPEN, False, True))             # 1 -> 3 only
    if with_return:
        g.add_edge(Edge(3, 3, 1, 50, 2, back_fuel, 1, EdgeStatus.OPEN, False, True))         # 3 -> 1 only
    g.finalize()
    return g


class RecommendRoundTripTests(unittest.TestCase):
    """Regression: the detour must be a real, affordable round trip on the directed graph."""

    def _run(self, g, fuel, nitro=1):
        from src.core.models import Racer
        from src.routing.planner import plan_route
        plan = plan_route(g, 0, [1], 2)
        self.assertTrue(plan.found)
        self.assertAlmostEqual(plan.fuel, 20.0)
        return recommend_pickups(g, plan, Racer(0, "me", True, "human", 0, fuel, nitro, 1, 1, 0.0), "Balanced")

    def test_no_return_edge_means_never_recommended(self):
        g = _spur_graph(0, with_return=False)
        self.assertEqual(self._run(g, 100.0), [])                  # plenty of fuel, but the car could never come back

    def test_expensive_return_priced_correctly(self):
        g = _spur_graph(back_fuel=20.0)                            # out 5 + back 20 = 25 (old estimate was 2*5 = 10)
        self.assertEqual(self._run(g, 40.0), [])                   # spare 20 < 25
        self.assertEqual(self._run(g, 44.9), [])                   # spare 24.9 < 25
        self.assertEqual(self._run(g, 45.0), [3])                  # spare 25 == 25

    def test_cheap_symmetric_round_trip_still_recommended(self):
        g = _spur_graph(back_fuel=5.0)
        self.assertEqual(self._run(g, 30.0), [3])                  # spare 10 == out 5 + back 5

    def test_blocked_return_road_removes_recommendation(self):
        from src.core.models import EdgeStatus
        g = _spur_graph(back_fuel=5.0)
        g.block_edge(3)
        self.assertEqual(self._run(g, 100.0), [])

    def test_full_nitro_or_inactive_pickup_or_no_spare_fuel(self):
        g = _spur_graph(back_fuel=5.0)
        self.assertEqual(self._run(g, 100.0, nitro=K.MAX_NITRO), [])
        self.assertEqual(self._run(g, 20.0), [])                   # exactly the route fuel: nothing spare
        g.set_station_active(3, False)
        self.assertEqual(self._run(g, 100.0), [])

    def test_pickup_on_the_route_costs_nothing(self):
        from src.core.graph import Graph
        from src.core.models import Vertex, Edge, VertexType as VT, EdgeStatus, Racer
        from src.routing.planner import plan_route
        g = Graph("on-route")
        for i, (t, o) in enumerate([(VT.START, None), (VT.NITRO_PICKUP, None), (VT.CHECKPOINT, 1), (VT.FINISH, None)]):
            g.add_vertex(Vertex(i, i * 100, 0, t, o))
        for i in range(3):
            g.add_edge(Edge(i, i, i + 1, 100, 3, 10.0, 1, EdgeStatus.OPEN, False, False))
        g.finalize()
        plan = plan_route(g, 0, [2], 3)
        r = Racer(0, "me", True, "human", 0, plan.fuel, 1, 1, 1, 0.0)             # zero spare fuel
        self.assertEqual(recommend_pickups(g, plan, r, "Balanced"), [1])

    def test_total_recommended_detour_fits_spare_fuel(self):
        g = load_circuit()
        from src.core.models import Racer
        from src.routing.planner import plan_route, route_vertices
        from src.planning.recommend import round_trips
        s, f = g.start_vertex(), g.finish_vertex()
        plan = plan_route(g, s, g.checkpoints_in_order(), f)
        for fuel in (30.0, 60.0, 100.0):
            r = Racer(0, "me", True, "human", s, fuel, 1, 1, 1, 0.0)
            ids = recommend_pickups(g, plan, r, "Balanced")
            trips = round_trips(g, list(dict.fromkeys(route_vertices(plan))), ids)
            self.assertEqual(set(trips), set(ids))
            self.assertLessEqual(sum(trips[i][0] for i in ids), max(0.0, fuel - plan.fuel) + 1e-6)
            self.assertLessEqual(len(ids), K.MAX_NITRO - 1)


def load_circuit():
    from src.core.track_io import load_track
    return load_track(os.path.join(os.path.dirname(__file__), "..", "tracks", "circuit1.json"))


if __name__ == "__main__":
    unittest.main()
