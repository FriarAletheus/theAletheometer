import importlib.util
import os


def load_ptm_module():
    """Load the ptm module from the scripts directory."""
    path = os.path.join(os.path.dirname(__file__), "..", "scripts", "ptm.py")
    spec = importlib.util.spec_from_file_location("ptm", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ptm_basic_step():
    ptm_module = load_ptm_module()
    machine = ptm_module.PolychronologicalTuringMachine()
    machine.write_to_dimension(0, "◇")
    machine.step()
    assert machine.current_state is not None
    assert len(machine.tapes[0]) > 0


