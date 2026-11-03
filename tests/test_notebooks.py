"""Execute every notebook through nbclient. Fail on any error or on a code cell with no output."""
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))
EXPECTED = [
    "01_memory_model_and_mutability",
    "02_typing_generics_protocols",
    "03_iterators_and_generators",
    "04_decorators_and_context_managers",
    "05_oop_dunders_dataclasses_patterns",
    "06_concurrency_gil_asyncio_processes",
    "07_arrays_and_hash_tables",
    "08_trees_heaps_tries",
    "09_graphs_and_shortest_paths",
    "10_dynamic_programming",
    "11_complexity_benchmarks",
]


def test_notebook_set_matches_curriculum():
    assert [p.stem for p in NOTEBOOKS] == EXPECTED


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_pins_python_313(path):
    nb = nbformat.read(path, as_version=4)
    assert nb.metadata["kernelspec"]["name"] == "python3"
    assert nb.metadata["language_info"]["version"].startswith("3.13")


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_executes_with_visible_output(path):
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=240, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}})
    client.execute()
    code = [c for c in nb.cells if c.cell_type == "code"]
    assert code
    silent = [i for i, c in enumerate(nb.cells) if c.cell_type == "code" and not c.outputs]
    assert not silent, f"code cells without output: {silent}"
