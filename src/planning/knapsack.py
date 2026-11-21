"""0/1 knapsack (DP with reconstruction), ratio greedy and an exhaustive checker."""
import time
from fractions import Fraction
from ..core.results import KnapsackResult


def _check(costs, benefits, budget):
    if len(costs) != len(benefits):
        raise ValueError("costs and benefits must have the same length")
    if budget < 0 or any(c < 0 for c in costs):
        raise ValueError("budget and costs must be non-negative integers")


def knapsack_dp(costs, benefits, budget, trace=None):
    """dp[i][b] = best benefit using the first i items with budget b. O(m*B) time and space (pseudo-polynomial).
    trace: optional list, receives a copy of dp row i after each item (used by the Algorithm Lab panel)."""
    t0 = time.perf_counter()
    _check(costs, benefits, budget)
    m = len(costs)
    dp = [[0] * (budget + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        c, v, prev, cur = costs[i - 1], benefits[i - 1], dp[i - 1], dp[i]
        for b in range(budget + 1):
            cur[b] = prev[b]
            if c <= b and prev[b - c] + v > cur[b]:
                cur[b] = prev[b - c] + v
        if trace is not None:
            trace.append(list(cur))
    chosen, b = [], budget
    for i in range(m, 0, -1):
        if dp[i][b] != dp[i - 1][b]:
            chosen.append(i - 1)
            b -= costs[i - 1]
    chosen.reverse()
    return KnapsackResult(best_value=dp[m][budget], chosen_ids=chosen, total_cost=sum(costs[i] for i in chosen),
                          dp_states=m * (budget + 1), runtime_s=time.perf_counter() - t0)


def greedy_select(costs, benefits, budget):
    """Zero-cost positive-benefit items first, zero-cost zero-benefit items skipped, then ratio desc (ties: lower index)."""
    t0 = time.perf_counter()
    _check(costs, benefits, budget)
    chosen, left, value = [], budget, 0
    rest = []
    for i, (c, v) in enumerate(zip(costs, benefits)):
        if c == 0 and v > 0:
            chosen.append(i)
            value += v
        elif c > 0 and v > 0:
            rest.append(i)
    rest.sort(key=lambda i: (-Fraction(benefits[i], costs[i]), i))
    for i in rest:
        if costs[i] <= left:
            chosen.append(i)
            left -= costs[i]
            value += benefits[i]
    chosen.sort()
    return KnapsackResult(best_value=value, chosen_ids=chosen, total_cost=sum(costs[i] for i in chosen),
                          dp_states=0, runtime_s=time.perf_counter() - t0)


def knapsack_bruteforce(costs, benefits, budget):
    """Exhaustive search over all 2^m subsets (m <= 22). Used only to verify the DP."""
    _check(costs, benefits, budget)
    m = len(costs)
    if m > 22:
        raise ValueError("bruteforce limited to 22 items")
    best = 0
    for mask in range(1 << m):
        c = v = 0
        for i in range(m):
            if (mask >> i) & 1:
                c += costs[i]
                v += benefits[i]
        if c <= budget and v > best:
            best = v
    return best
