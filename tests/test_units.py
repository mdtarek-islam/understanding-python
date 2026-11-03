import random

import pytest

from understanding_python import algorithms as al
from understanding_python import dp, functional as fn, graphs as gr, internals as it
from understanding_python import patterns as pt
from understanding_python import structures as st


# internals
def test_refcount_grows_with_new_name():
    x = object()
    before = it.refcount(x)
    y = x
    assert it.refcount(x) == before + 1
    assert it.same_object(x, y)


def test_deep_size_exceeds_shallow():
    data = {"a": [1, 2, 3], "b": ["x" * 100]}
    import sys

    assert it.deep_size(data) > sys.getsizeof(data)


def test_opnames_contains_return():
    assert any("RETURN" in n for n in it.opnames(lambda a: a + 1))
    assert "BINARY" in it.disassemble(lambda a: a + 1) or "ADD" in it.disassemble(lambda a: a + 1)


def test_cycle_needs_gc():
    it.Tracked.reclaimed.clear()
    it.make_cycle("c")
    assert it.collect() >= 2
    assert {"c-a", "c-b"} <= set(it.Tracked.reclaimed)


# functional
def test_counter_closures_are_independent():
    a, b = fn.make_counter(), fn.make_counter(10)
    assert (a(), a(), b()) == (1, 2, 11)


def test_memoize_and_repeat():
    calls = []

    @fn.memoize
    def sq(x):
        calls.append(x)
        return x * x

    assert sq(4) == sq(4) == 16 and calls == [4]

    @fn.repeat(3)
    def hi():
        return "hi"

    assert hi() == ["hi"] * 3 and hi.__name__ == "hi"


def test_generators_and_iterators():
    assert list(fn.fib_gen(30)) == [0, 1, 1, 2, 3, 5, 8, 13, 21]
    m = fn.running_mean()
    next(m)
    assert m.send(2) == 2 and m.send(4) == 3
    assert list(fn.Countdown(3)) == [3, 2, 1]


def test_context_managers():
    out = {}
    with pytest.raises(ValueError):
        with fn.timer(out):
            raise ValueError
    assert out["elapsed"] >= 0
    with fn.Suppress(KeyError):
        {}["x"]
    with pytest.raises(TypeError):
        with fn.Suppress(KeyError):
            raise TypeError


# patterns
def test_vector_dunders():
    v = pt.Vector(3, 4)
    assert abs(v) == 5 and v + v == pt.Vector(6, 8) and 2 * v == pt.Vector(6, 8)
    assert not pt.Vector(0, 0) and hash(v) == hash(pt.Vector(3, 4))
    assert repr(v) == "Vector(3, 4)"


def test_dataclasses_and_abc():
    assert pt.Point(1, 2) < pt.Point(1, 3)
    c1, c2 = pt.Cart(), pt.Cart()
    c1.add("a")
    assert c2.items == []
    with pytest.raises(TypeError):
        pt.Shape()
    assert pt.total_area([pt.Rect(2, 3), pt.Rect(1, 1)]) == 7
    assert pt.factory("rect").area() == 6
    with pytest.raises(ValueError):
        pt.factory("hex")


def test_strategy_observer_singleton():
    assert pt.Checkout(pt.Percent(10)).total([50, 50]) == 90
    assert pt.Checkout(pt.NoDiscount()).total([1.5]) == 1.5
    bus, got = pt.EventBus(), []
    bus.subscribe("t", got.append)
    assert bus.publish("t", 1) == 1 and got == [1]
    assert pt.Singleton() is pt.Singleton()


# structures
def test_linked_list():
    ll = st.LinkedList()
    for i in range(4):
        ll.push_front(i)
    assert list(ll) == [3, 2, 1, 0]
    ll.reverse()
    assert list(ll) == [0, 1, 2, 3]
    assert ll.remove(0) and ll.remove(2) and not ll.remove(9)
    assert list(ll) == [1, 3] and len(ll) == 2


def test_stack_queue_balanced():
    s = st.Stack()
    s.push(1)
    assert s.peek() == 1 and s.pop() == 1
    with pytest.raises(IndexError):
        s.pop()
    q = st.Queue()
    q.enqueue(1), q.enqueue(2)
    assert q.dequeue() == 1 and len(q) == 1
    q.dequeue()
    with pytest.raises(IndexError):
        q.dequeue()
    assert st.balanced("{[()]}") and not st.balanced("(]") and not st.balanced("(")


def test_heap_matches_sorted():
    rng = random.Random(1)
    data = [rng.randint(0, 99) for _ in range(200)]
    h = st.MinHeap()
    for x in data:
        h.push(x)
    assert [h.pop() for _ in range(len(h))] == sorted(data)
    with pytest.raises(IndexError):
        h.pop()


def test_hashmap_matches_dict():
    rng = random.Random(2)
    m, ref = st.HashMap(), {}
    for _ in range(500):
        k, v = rng.randint(0, 80), rng.random()
        m.put(k, v)
        ref[k] = v
    assert len(m) == len(ref) and m.capacity > 8
    assert all(m.get(k) == v for k, v in ref.items())
    assert m.delete(next(iter(ref))) and m.get("none", 7) == 7 and not m.delete("none")


def test_bst_and_avl():
    keys = list(range(200))
    b, a = st.BST(), st.AVLTree()
    for k in keys:
        b.insert(k)
        a.insert(k)
    assert b.height() == 200
    assert a.height() <= 11 and a.is_balanced()
    assert b.inorder() == a.inorder() == keys
    assert 5 in b and 5 in a and 500 not in b and 500 not in a
    b.insert(5)


def test_avl_random_and_rotations():
    rng = random.Random(3)
    ks = rng.sample(range(1000), 300)
    a = st.AVLTree()
    for k in ks:
        a.insert(k)
    assert a.inorder() == sorted(ks) and a.is_balanced()
    z = st.AVLTree()
    for k in (3, 1, 2):  # left-right case
        z.insert(k)
    assert z.root.k == 2
    z = st.AVLTree()
    for k in (1, 3, 2):  # right-left case
        z.insert(k)
    assert z.root.k == 2


def test_trie_and_union_find():
    t = st.Trie()
    for w in ("car", "card", "care", "dog"):
        t.insert(w)
    assert t.search("car") and not t.search("ca") and t.starts_with("ca")
    assert t.with_prefix("car") == ["car", "card", "care"] and t.with_prefix("x") == []
    uf = st.UnionFind(6)
    assert uf.union(0, 1) and uf.union(1, 2) and not uf.union(0, 2)
    assert uf.find(0) == uf.find(2) and uf.components == 4


# algorithms
@pytest.mark.parametrize("sorter", [al.insertion_sort, al.merge_sort, al.quick_sort, al.heap_sort])
def test_sorters(sorter):
    rng = random.Random(4)
    for n in (0, 1, 2, 50):
        d = [rng.randint(-20, 20) for _ in range(n)]
        assert sorter(d) == sorted(d)
    assert sorter([5, 5, 5]) == [5, 5, 5]


def test_counting_and_search():
    assert al.counting_sort([3, 1, 2, 1], 4) == [1, 1, 2, 3]
    assert al.is_sorted([1, 2, 2]) and not al.is_sorted([2, 1])
    a = [1, 3, 5, 7]
    assert al.binary_search(a, 5) == 2 and al.binary_search(a, 4) == -1
    assert al.binary_search([], 1) == -1 and al.lower_bound(a, 4) == 2
    assert al.search_on_answer(lambda x: x * x >= 50, 0, 100) == 8
    assert al.search_on_answer(lambda x: False, 0, 5) == 6


def test_comparison_counts_scale():
    d = list(range(256))
    random.Random(5).shuffle(d)
    c = al.count_comparisons(al.merge_sort, d)
    assert c <= 256 * 8


# graphs
G = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
W = {"a": [("b", 1), ("c", 4)], "b": [("c", 2), ("d", 6)], "c": [("d", 3)], "d": []}


def test_bfs_dfs():
    assert gr.bfs(G, "a") == {"a": 0, "b": 1, "c": 1, "d": 2}
    assert gr.dfs(G, "a") == ["a", "b", "d", "c"]


def test_dijkstra():
    dist, prev = gr.dijkstra(W, "a")
    assert dist == {"a": 0, "b": 1, "c": 3, "d": 6}
    assert gr.path_to(prev, "a", "d") == ["a", "b", "c", "d"]
    with pytest.raises(ValueError):
        gr.dijkstra({"a": [("b", -1)]}, "a")


def test_topo_and_kruskal():
    order = gr.topological_sort(G)
    assert order.index("a") < order.index("b") < order.index("d")
    with pytest.raises(ValueError):
        gr.topological_sort({"x": ["y"], "y": ["x"]})
    total, used = gr.kruskal(4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4)])
    assert total == 7 and len(used) == 3


# dp
def test_dp():
    assert dp.lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4 and dp.lis_length([]) == 0
    rng = random.Random(6)
    for _ in range(30):
        a = [rng.randint(0, 20) for _ in range(rng.randint(0, 15))]
        assert dp.lis_length(a) == dp.lis_quadratic(a)
        w = [rng.randint(1, 8) for _ in range(8)]
        v = [rng.randint(1, 20) for _ in range(8)]
        assert dp.knapsack(w, v, 15) == dp.knapsack_brute(w, v, 15)
    assert dp.edit_distance("kitten", "sitting") == 3 and dp.edit_distance("", "abc") == 3
    assert dp.fib_naive(15) == dp.fib_memo(15) == dp.fib_table(15) == 610
