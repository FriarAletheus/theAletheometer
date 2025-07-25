import json
import os
import sys
from pathlib import Path

import importlib
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aletheo_file_logger as fl


@pytest.fixture(autouse=True)
def restore_cwd(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(cwd)


def read_entries(log_dir: Path):
    logs = list(log_dir.glob("*.log"))
    entries = []
    for log in logs:
        with open(log) as f:
            for line in f:
                entries.append(json.loads(line))
    return entries


def test_import_logged(tmp_path):
    sys.path.insert(0, str(tmp_path))
    (tmp_path / "dummy.py").write_text("x = 1\n")
    fl.install()
    import dummy  # noqa: F401
    fl.remove()
    sys.path.remove(str(tmp_path))
    entries = read_entries(tmp_path / "logs")
    files = [Path(e["file"]) for e in entries if e["action"] == "import"]
    assert (tmp_path / "dummy.py").resolve() in files


def test_open_logged(tmp_path):
    fl.install()
    p = Path("afile.txt")
    with open(p, "w") as f:
        f.write("hi")
    with open(p, "r") as f:
        _ = f.read()
    fl.remove()
    entries = read_entries(tmp_path / "logs")
    modes = [e["mode"] for e in entries if Path(e["file"]) == p.resolve()]
    assert "w" in modes and "r" in modes


def test_remove_restores(tmp_path):
    fl.install()
    fl.remove()
    log_dir = tmp_path / "logs"
    size_before = sum(f.stat().st_size for f in log_dir.glob("*.log")) if log_dir.exists() else 0
    with open("after.txt", "w") as f:
        f.write("x")
    importlib.import_module("math")
    size_after = sum(f.stat().st_size for f in log_dir.glob("*.log")) if log_dir.exists() else 0
    assert size_before == size_after
