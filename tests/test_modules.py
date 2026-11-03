"""Unit tests for the modules added in the deep curriculum: typing, oop, hashing, heaps, trees,
pathfinding, concurrency, bench and the extra dynamic programming helpers."""
import asyncio
import heapq
import math
import random

import pytest

from understanding_python import bench, concurrency as cc, dp, functional as fn, hashing as hs
from understanding_python import heaps as hp, oop, pathfinding as pf, trees as tr, typing_tools as tt


# typing_tools
def test_typed_stack_and_type_params():
    s = tt.TypedStack([1, 2])
    s.push(3)
    assert s.pop() == 3 and s.peek() == 2 and list(s) == [2, 1] and len(s) == 2
    assert [p.__name__ for p in tt.TypedStack.__type_params__] == ["T"]
    with pytest.raises(IndexError):
        tt.TypedStack().pop()
    with pytest.raises(IndexError):
        tt.TypedStack().peek()


def test_bounded_and_constrained_generics():
    assert tt.max_of([3, 9, 4]) == 9 and tt.max_of(["b", "a"]) == "b"
    with pytest.raises(ValueError):
        tt.max_of([])
    assert tt.first_or([], "none") == "none" and tt.first_or("xyz", "") == "x"
    assert tt.concat("a", "b") == "ab" and tt.concat(b"a", b"b") == b"ab"
    assert tt.Pair.__value__ == tuple[tt.Pair.__type_params__[0], tt.Pair.__type_params__[1]]


def test_protocols_are_structural():
    class Conn:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    c = Conn()
    assert isinstance(c, tt.Closeable) and not isinstance(42, tt.Closeable)
    assert tt.close_all([c, 42, "x"]) == ["int", "str"] and c.closed
    repo = tt.InMemoryRepository()
    assert tt.cache_user(repo, "u1", {"name": "Ada"}) == {"name": "Ada"}
    assert tt.cache_user(repo, "u1", {"name": "other"}) == {"name": "Ada"}


# functional additions
def test_retry_recovers_and_reraises():
    calls = []

    @fn.retry(attempts=3, exceptions=(ConnectionError,))
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("down")
        return "ok"

    assert flaky() == "ok" and len(calls) == 3

    @fn.retry(attempts=2)
    def broken():
        raise KeyError("x")

    with pytest.raises(KeyError):
        broken()
    with pytest.raises(ValueError):
        fn.retry(attempts=0)


def test_chunked_and_log_parsing():
    assert list(fn.chunked(range(5), 2)) == [[0, 1], [2, 3], [4]] and list(fn.chunked([], 3)) == []
    with pytest.raises(ValueError):
        list(fn.chunked([1], 0))
    lines = [
        "2026-02-03 10:00:01 ERROR payments card declined id=9",
        "garbage",
        "2026-02-03 10:00:02 INFO search ok",
    ]
    assert fn.parse_log_line("garbage") is None
    recs = list(fn.log_records(lines))
    assert [r["service"] for r in recs] == ["payments", "search"]
    assert [r["level"] for r in fn.log_records(lines, level="ERROR")] == ["ERROR"]


def test_transaction_rolls_back():
    store = {"balance": 100}
    with fn.Transaction(store) as s:
        s["balance"] -= 30
    assert store["balance"] == 70
    with pytest.raises(RuntimeError):
        with fn.Transaction(store) as s:
            s["balance"] = 0
            s["extra"] = 1
            raise RuntimeError
    assert store == {"balance": 70}


# patterns
def test_vector_rejects_foreign_operands():
    from understanding_python.patterns import Vector

    with pytest.raises(TypeError):
        Vector(1, 2) + 5
    with pytest.raises(TypeError):
        Vector(1, 2) * "a"
    assert Vector(1, 2) * 2 == 2 * Vector(1, 2) == Vector(2, 4)


# oop
def test_playlist_sequence_protocol():
    p = oop.Playlist(["a", "b", "c"])
    assert len(p) == 3 and p[1] == "b" and "c" in p and list(p) == ["a", "b", "c"]
    assert repr(p[:2]) == "Playlist(['a', 'b'])"
    assert list(reversed(p)) == ["c", "b", "a"]


def test_descriptor_validates_per_instance():
    a, b = oop.LineItem("sku1", 2, 9.99), oop.LineItem("sku2", 1, 5.0)
    assert a.subtotal == 19.98 and b.qty == 1
    with pytest.raises(ValueError, match="qty"):
        a.qty = 0
    with pytest.raises(ValueError):
        oop.LineItem("x", 1, -1.0)
    assert isinstance(oop.LineItem.qty, oop.Positive)


def test_order_record_is_frozen_and_slotted():
    o = oop.Order("A-1", "ada", (oop.OrderLine("pen", 3, 1.5), oop.OrderLine("pad", 1, 4.0)))
    assert o.total() == 8.5
    with pytest.raises(AttributeError):
        o.customer = "bob"
    assert not hasattr(o, "__dict__")


def test_slots_block_dynamic_attributes():
    assert hasattr(oop.PlainPoint(1, 2), "__dict__") and not hasattr(oop.SlotPoint(1, 2), "__dict__")
    with pytest.raises(AttributeError):
        oop.SlotPoint(1, 2).z = 3


def test_registry_and_state_machine():
    assert oop.PaymentMethod.create("card").fee(100) == 3.2
    assert oop.PaymentMethod.create("bank").fee(100) == 0.8
    with pytest.raises(ValueError, match="known"):
        oop.PaymentMethod.create("cash")
    sm = oop.OrderStateMachine()
    sm.move("paid")
    sm.move("shipped")
    with pytest.raises(ValueError):
        sm.move("cancelled")
    assert sm.history == ["placed", "paid", "shipped"]


# hashing
def test_dynamic_array_growth_and_insert():
    arr = hs.DynamicArray()
    for i in range(33):
        arr.append(i)
    assert len(arr) == 33 and arr.capacity == 64 and arr.resizes == [2, 4, 8, 16, 32, 64]
    arr.insert(0, -1)
    assert arr[0] == -1 and arr[1] == 0 and arr[-1] == 32 and len(arr) == 34
    with pytest.raises(IndexError):
        arr[34]
    with pytest.raises(IndexError):
        arr.insert(99, 0)
    with pytest.raises(ValueError):
        hs.DynamicArray(growth=1)


def test_open_addressing_matches_dict_under_churn():
    rng = random.Random(7)
    m, ref = hs.OpenAddressingMap(), {}
    for _ in range(3000):
        k = rng.randint(0, 120)
        if rng.random() < 0.3:
            assert m.delete(k) == (ref.pop(k, None) is not None)
        else:
            v = rng.random()
            m.put(k, v)
            ref[k] = v
    assert len(m) == len(ref)
    assert all(m.get(k) == v for k, v in ref.items())
    assert m.get(9999, "miss") == "miss"
    assert m.capacity >= len(ref) * 3 // 2


def test_lru_cache_evicts_oldest():
    c = hs.LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)
    assert c.get("b") is None and c.keys() == ["c", "a"]
    c.put("a", 10)
    assert c.get("a") == 10 and len(c) == 2 and (c.hits, c.misses) == (2, 1)
    with pytest.raises(ValueError):
        hs.LRUCache(0)


# heaps
def test_top_k_matches_sorted():
    rng = random.Random(8)
    items = [(f"p{i}", rng.random()) for i in range(500)]
    assert hp.top_k(items, 5) == sorted(items, key=lambda t: -t[1])[:5]
    assert hp.top_k(items, 0) == [] and len(hp.top_k(items[:3], 10)) == 3


def test_running_median_matches_statistics():
    import statistics

    rng = random.Random(9)
    rm, seen = hp.RunningMedian(), []
    with pytest.raises(ValueError):
        rm.median()
    for _ in range(200):
        x = rng.randint(0, 50)
        rm.add(x)
        seen.append(x)
        assert rm.median() == statistics.median(seen)


def test_merge_sorted_streams():
    a, b, c = [1, 4, 9], [2, 3, 10], []
    assert list(hp.merge_sorted_streams(a, b, c)) == list(heapq.merge(a, b, c)) == [1, 2, 3, 4, 9, 10]
    assert list(hp.merge_sorted_streams()) == []


def test_task_scheduler_priority_fifo_cancel():
    s = hp.TaskScheduler()
    s.add("backup", 5)
    s.add("email-1", 1)
    s.add("email-2", 1)
    s.add("report", 3)
    s.cancel("report")
    s.add("backup", 0)
    assert len(s) == 3
    assert [s.pop() for _ in range(3)] == ["backup", "email-1", "email-2"]
    with pytest.raises(IndexError):
        s.pop()


# trees
def test_tree_shapes_and_queries():
    keys = list(range(1, 16))
    root = tr.from_sorted(keys)
    assert tr.height(root) == 4 and tr.inorder(root) == keys and tr.is_valid_bst(root)
    assert tr.level_order(root)[0] == [8] and tr.level_order(None) == []
    assert tr.lowest_common_ancestor(root, 1, 3) == 2 and tr.lowest_common_ancestor(root, 9, 15) == 12
    assert tr.lowest_common_ancestor(None, 1, 2) is None
    chain = None
    for k in keys:
        chain = tr.insert_unbalanced(chain, k)
    assert tr.height(chain) == 15
    assert tr.insert_unbalanced(chain, 3) is chain
    root.left.key = 100
    assert not tr.is_valid_bst(root)


def test_deep_chain_does_not_hit_recursion_limit():
    root = None
    for k in range(3000):
        root = tr.insert_unbalanced(root, k)
    assert tr.height(root) == 3000 and tr.inorder(root)[-1] == 2999


# pathfinding
def test_roads_respect_heuristic_admissibility():
    g = pf.uk_road_graph()
    for a, edges in g.items():
        for b, km in edges:
            assert km >= pf.haversine_km(pf.CITY_COORDS[a], pf.CITY_COORDS[b]), (a, b)
            assert (a, km) in g[b]


def test_haversine_known_distance():
    d = pf.haversine_km(pf.CITY_COORDS["London"], pf.CITY_COORDS["Edinburgh"])
    assert 525 < d < 540


def test_astar_equals_dijkstra_and_expands_less():
    g = pf.uk_road_graph()
    goal = "Glasgow"
    h = lambda c: pf.haversine_km(pf.CITY_COORDS[c], pf.CITY_COORDS[goal])
    c1, p1, e1 = pf.astar(lambda n: g[n], "London", goal, h)
    c0, p0, e0 = pf.astar(lambda n: g[n], "London", goal, lambda n: 0)
    assert c1 == c0 and p1[0] == "London" and p1[-1] == goal and e1 <= e0
    assert pf.astar(lambda n: g[n], "London", "London", h)[:2] == (0.0, ["London"])


def test_astar_unreachable_and_negative():
    cost, path, _ = pf.astar(lambda n: [], "a", "b", lambda n: 0)
    assert cost == math.inf and path == []
    with pytest.raises(ValueError):
        pf.astar(lambda n: [("b", -1)], "a", "b", lambda n: 0)


def test_grid_search_around_wall():
    grid = ["....#", ".##.#", "...#.", ".#...", "....."]
    nb = pf.grid_neighbours(grid)
    cost, path, _ = pf.astar(nb, (0, 0), (4, 4), pf.manhattan((4, 4)))
    assert cost == 8 and path[0] == (0, 0) and path[-1] == (4, 4)
    sealed = ["..#.", "..#.", "..#."]
    assert pf.astar(pf.grid_neighbours(sealed), (0, 0), (0, 3), pf.manhattan((0, 3)))[0] == math.inf


# concurrency
def test_primes_and_split():
    assert cc.count_primes((0, 30)) == 10
    assert cc.split_range(0, 10, 3) == [(0, 4), (4, 7), (7, 10)]
    assert sum(cc.count_primes(r) for r in cc.split_range(0, 5000, 4)) == cc.count_primes((0, 5000))
    with pytest.raises(ValueError):
        cc.split_range(0, 10, 0)


def test_threads_overlap_blocking_io():
    _, seq = cc.timed(lambda: cc.run_sequential(cc.blocking_io, [0.05] * 6))
    _, par = cc.timed(lambda: cc.run_threads(cc.blocking_io, [0.05] * 6, workers=6))
    assert par < seq / 2


def test_asyncio_gather_and_blocking_call():
    assert asyncio.run(cc.gather_io([0.01, 0.02, 0.01], limit=2)) == [0.01, 0.02, 0.01]
    blocked = asyncio.run(cc.ticks_during(cc.sleep_blocking_100ms, offload=False))
    free = asyncio.run(cc.ticks_during(cc.sleep_blocking_100ms, offload=True))
    assert free > blocked


def test_lost_updates_only_without_lock():
    assert cc.hammer(4, 2000, locked=True) == 8000
    assert cc.hammer(4, 2000, locked=False) <= 8000
    assert cc.hammer(4, 500, locked=True, pause=True) == 2000
    assert cc.hammer(4, 500, locked=False, pause=True) < 2000


def test_process_pool_runs_worker_from_module():
    out = cc.run_processes(cc.count_primes, [(0, 100), (100, 200)], workers=2)
    assert out == [25, 21]


# bench
def test_fit_exponent_recovers_known_growth():
    linear = [(n, 2e-6 * n) for n in (100, 200, 400, 800)]
    quad = [(n, 1e-9 * n * n) for n in (100, 200, 400, 800)]
    assert abs(bench.fit_exponent(linear) - 1) < 1e-9
    assert abs(bench.fit_exponent(quad) - 2) < 1e-9
    assert bench.classify(0.05).startswith("O(1)") and bench.classify(2.0).startswith("about O(n^2)")
    assert bench.classify(1.1) == "O(n) or O(n log n)" and bench.classify(1.5).startswith("between")
    with pytest.raises(ValueError):
        bench.fit_exponent([(10, 1.0)])


def test_scaling_table_shape():
    rows = bench.scaling_table(sum, lambda n: list(range(n)), [10, 100], number=5)
    assert [n for n, _ in rows] == [10, 100] and all(t > 0 for _, t in rows)


# dp extras
def test_dp_extras():
    assert dp.fib_calls(10) == 177 and dp.fib_calls(1) == 1
    assert dp.min_coins([1, 3, 4], 6) == 2 and dp.min_coins([2], 3) == -1 and dp.min_coins([5], 0) == 0
    with pytest.raises(ValueError):
        dp.min_coins([1], -1)
    assert dp.lcs("ABCBDAB", "BDCABA") in {"BCBA", "BDAB", "BCAB"} and len(dp.lcs("ABCBDAB", "BDCABA")) == 4
    assert dp.lcs("", "abc") == "" and dp.lcs("abc", "xyz") == ""
    assert dp.word_break("catsanddog", {"cat", "cats", "and", "sand", "dog"}) in (
        ["cats", "and", "dog"], ["cat", "sand", "dog"])
    assert dp.word_break("catsandog", {"cats", "dog", "sand", "and", "cat"}) is None
    assert dp.word_break("", {"a"}) == [] and dp.word_break("a", set()) is None
