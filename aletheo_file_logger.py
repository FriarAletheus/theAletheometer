"""File access logger for The Alethiometer.

This module records every file opening and module import while enabled.
It monkey-patches :func:`builtins.open` and registers a profiling
callback to track imports via ``importlib`` internals. Logged events are
written asynchronously as JSON lines to ``./logs``. The design targets
less than 5%% overhead in a synthetic benchmark of 100000 trivial calls
by deferring disk writes to a background thread.
"""

from __future__ import annotations

import builtins
import datetime as _dt
import importlib
import inspect
import traceback
import json
import logging
import os
import sys
from pathlib import Path
from queue import SimpleQueue
from threading import Thread
from typing import Any, Callable, Dict, List, Optional

__all__ = ["install", "remove"]

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

_original_open = builtins.open
_original_profile: Optional[Callable[..., Any]] = None

_find_load_code = importlib._bootstrap._find_and_load.__code__
_find_load_unlocked_code = importlib._bootstrap._find_and_load_unlocked.__code__

_queue: SimpleQueue[Dict[str, Any]] = SimpleQueue()
_writer_thread: Optional[Thread] = None
_log_file: Optional[Any] = None
_log_dir = Path("logs")
_file_index = 0
_installed = False
_sentinel = object()


def _current_timestamp() -> str:
    return _dt.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


def _capture_stack(skip: int = 2, limit: int = 10) -> List[str]:
    summary = traceback.extract_stack()[:-skip]
    return [
        f"{Path(f.filename).stem}.{f.name or '<unknown>'}"
        for f in summary[-limit:]
    ][::-1]


def _log_record(action: str, file_path: str, mode: Optional[str]) -> None:
    record = {
        "ts": _current_timestamp(),
        "action": action,
        "file": file_path,
        "mode": mode,
        "caller": _capture_stack(3, 1)[0],
        "stack": _capture_stack(),
    }
    _queue.put(record)


def _ensure_log_file() -> None:
    """Create or rotate the current log file."""
    global _log_file, _file_index
    _log_dir.mkdir(exist_ok=True)
    base = _dt.date.today().isoformat()

    if _log_file is None:
        path = _log_dir / f"{base}.log"
        while path.exists() and path.stat().st_size > 10_000_000:
            _file_index += 1
            path = _log_dir / f"{base}_{_file_index}.log"
    else:
        if _log_file.tell() <= 10_000_000:
            return
        _log_file.close()
        _file_index += 1
        path = _log_dir / f"{base}_{_file_index}.log"

    _log_file = open(path, "a", encoding="utf-8")


def _writer() -> None:
    while True:
        record = _queue.get()
        if record is _sentinel:
            break
        try:
            _ensure_log_file()
            if _log_file is not None:
                _log_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                _log_file.flush()
        except Exception as exc:  # pragma: no cover - unexpected failures
            _logger.warning("Failed to write log record: %s", exc)


def _patched_open(file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
    path = os.fspath(file) if isinstance(file, (str, bytes, os.PathLike)) else str(file)
    abs_path = os.path.abspath(path)
    _log_record("open", abs_path, mode[:1])
    return _original_open(file, mode, *args, **kwargs)


def _profile(frame: Any, event: str, arg: Any) -> Optional[Callable]:
    if event == "return" and frame.f_code in {_find_load_code, _find_load_unlocked_code}:
        module = arg
        file = getattr(module, "__file__", module.__name__)
        file_path = os.path.abspath(file) if file else module.__name__
        _log_record("import", file_path, None)
    return _profile


def install() -> None:
    """Activate file-access logging."""
    global _writer_thread, _installed, _original_profile
    if _installed:
        raise RuntimeError("File logger already installed")
    try:
        _original_profile = sys.getprofile()
        builtins.open = _patched_open
        sys.setprofile(_profile)
        _writer_thread = Thread(target=_writer, daemon=True)
        _writer_thread.start()
        _installed = True
    except Exception as exc:
        remove()
        raise RuntimeError(f"Failed to install file logger: {exc}") from exc


def remove() -> None:
    """Deactivate file-access logging and restore original behaviour."""
    global _writer_thread, _log_file, _installed
    if not _installed:
        return
    builtins.open = _original_open
    sys.setprofile(_original_profile)
    _queue.put(_sentinel)
    if _writer_thread is not None:
        _writer_thread.join()
        _writer_thread = None
    if _log_file is not None:
        _log_file.close()
        _log_file = None
    _installed = False


def _self_test() -> None:
    install()
    with open("self_test.tmp", "w") as fh:
        fh.write("test")
    import math  # noqa: F401
    remove()
    for log_file in _log_dir.glob("*.log"):
        print(log_file.read_text())


if __name__ == "__main__":
    _self_test()
