<p align="center"><img src="docs/readme-cover-img.webp" alt="understanding-python cover" width="100%"></p>

# understanding-python

## 1. Overview
Eight executable notebooks that teach how Python works inside and how classic data structures and algorithms behave.
Each notebook states learning goals, explains the idea, runs code, checks it with assertions, and proves the cost.
A tested package, `understanding_python`, holds the implementations the notebooks import.

## 2. Architecture
![Curriculum map](assets/architecture.svg)

Notebooks import from `src/understanding_python/`. Unit tests cover the package. A second test executes every notebook.
For the call structure of Dijkstra, see `assets/call-graph-dijkstra.svg`.

![Dijkstra call graph](assets/call-graph-dijkstra.svg)

## 3. Features
1. CPython internals: object model, reference counting, interning, the cyclic collector, `sys.getsizeof`, `dis`.
2. Closures, decorators, iterators, generators and context managers.
3. Dunder methods, dataclasses, ABCs and SOLID patterns.
4. Lists, heaps, hash maps, BST, AVL tree, trie and union-find built from scratch.
5. Sorting proofs, binary search, BFS, DFS, Dijkstra, Kruskal, LIS, knapsack and edit distance.

## 4. Quick start
1. Create a virtual environment: `python -m venv .venv`
2. Install: `pip install -e .[dev]`
3. Run the tests: `pytest`
4. Open a notebook: `jupyter lab notebooks/`

## 5. Configuration
1. Python 3.10 or newer. CI uses 3.12.
2. Dependencies live in `pyproject.toml` and `requirements.txt`.
3. Benchmarks use fixed seeds and small sizes. Each notebook runs in seconds.
4. The notebooks add `src/` to `sys.path`, so they run without installation.

## 6. Usage
```python
from understanding_python.graphs import dijkstra
dist, prev = dijkstra({"s": [("a", 2)], "a": []}, "s")
assert dist["a"] == 2
```
Read the notebooks in order, 01 to 08. Run `pytest tests/test_notebooks.py` to execute all of them.

## 7. Licence and contribution
MIT licence. See `LICENSE`. Open an issue before a large change. Add a test with every new function.

## 8. Maintenance status
Experimental. The curriculum is complete for its first release and gets updates as time allows.
