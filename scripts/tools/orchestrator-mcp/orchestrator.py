#!/usr/bin/env python3
"""
Orchestrator-mcp
═══════════════════════════════════════════════════════════════════
Stateful orchestration layer for PCTM execution with oracle integration.

Responsibilities:
- Session state management
- File permission gating based on execution phase
- Oracle trigger coordination
- Revision lifecycle management
- Comprehensive audit logging

States:
  INIT: Initial dimensional vector input
  COMPUTE: PCTM execution in progress
  ORACLE_CONSULT: MV threshold breached, oracle consultation active
  REVISION: Oracle guidance received, revision being formulated
  COMPLETE: Session complete

File Permissions by State:

INIT:
  - UCCanon.json (r--) reference ONLY
  - input.json (rw-) LLM provides initial state

ORACLE_CONSULT:
  - UCCanon.json (r--) reference ONLY
  - MDCanon.json (r--) reference ONLY
  - Orders_Mathematical_Substrate.json (r--) reference ONLY
  - oracle_result.json (r--) oracle output
  - revision.json (-w-) LLM writes proposed changes

ALL STATES:
  - output.json (-w-) APPEND-ONLY audit log (ONLY writable file!)
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import importlib.util

def _load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Canonical workspace paths (shared contract across dev + Docker)
os.environ["ICHING_JSON"] = str(Path(__file__).parent / "workspace" / "iching.json")

# Deterministic module loading (no cwd, no repo-relative sys.path)
# Prefer explicit env vars; otherwise prefer local repo layout; otherwise Docker layout.

_here = Path(__file__).resolve().parent

_PCTM_PY = os.environ.get("PCTM_PY") or (
    str(_here.parent / "PCTM-mcp" / "PCTM.py")
    if (_here.parent / "PCTM-mcp" / "PCTM.py").exists()
    else "/app/PCTM-mcp/PCTM.py"
)
_ICHIRAN_PY = os.environ.get("ICHIRAN_PY") or (
    str(_here.parent / "iching-mcp" / "ichiRan.py")
    if (_here.parent / "iching-mcp" / "ichiRan.py").exists()
    else "/app/iching-mcp/ichiRan.py"
)


pctm_mod = _load_module_from_path("pctm_mod", _PCTM_PY)
ichiran_mod = _load_module_from_path("ichiran_mod", _ICHIRAN_PY)

PCTMEngine = pctm_mod.PCTMEngine
DimensionalState = pctm_mod.DimensionalState
ichiRan = ichiran_mod

class OrchestratorState(Enum):
    INIT = "init"
    COMPUTE = "compute"
    ORACLE_CONSULT = "oracle_consult"
    REVISION = "revision"
    COMPLETE = "complete"


@dataclass
class SessionContext:
    """Stateful session context."""
    session_id: str
    state: OrchestratorState
    current_dimensional_state: Optional[Dict] = None
    mv_history: List[Dict] = None
    oracle_consultations: List[Dict] = None
    revisions_applied: List[Dict] = None
    started_at: str = None

    def __post_init__(self):
        if self.mv_history is None:
            self.mv_history = []
        if self.oracle_consultations is None:
            self.oracle_consultations = []
        if self.revisions_applied is None:
            self.revisions_applied = []
        if self.started_at is None:
            self.started_at = datetime.utcnow().isoformat()


app = Server("state-orchestrator-mcp")

# Global session context
_session: Optional[SessionContext] = None
_work_dir = Path(__file__).parent / "workspace"
_work_dir.mkdir(exist_ok=True)


def _log_to_output(entry: Dict[str, Any]):
    """Append to output.json audit log."""
    output_file = _work_dir / "output.json"

    if output_file.exists():
        with open(output_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"sessions": []}

    entry["timestamp"] = datetime.utcnow().isoformat()
    data["sessions"].append(entry)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)


# Dev singleton engine
_pctm_engine = None

def _get_pctm_engine():
    global _pctm_engine
    if _pctm_engine is None:
        _pctm_engine = PCTMEngine(
            uc_path=str(_work_dir / "UCCanon.json"),
            md_path=str(_work_dir / "MDCanon.json"),
            orders_path=str(_work_dir / "Orders_Mathematical_Substrate.json"),
            oracle_enabled=False,
            fallback_policy="identity",
            verbose=False,
        )

    return _pctm_engine

def _call_pctm_tool(tool_name: str, args: Dict) -> Dict:
    """
    DEV MODE: Call PCTM functionality directly instead of via MCP subprocess.
    """
    engine = _get_pctm_engine()

    if tool_name == "pctm_compute_step":
        state_dict = args.get("state", {})
        state = DimensionalState.from_dict(state_dict)
        applied_modes, new_state = engine.step(state)

        mvresults = engine.history["mv_results"][-1] if engine.history["mv_results"] else {}
        successes = sum(1 for r in mvresults.values() if r.get("mv", 0) == 1.0)
        total = len(mvresults) if mvresults else 1
        mvsuccessrate = successes / total

        oracle_fired = bool(engine.history["oracle_invocations"])
        oracle_result = engine.history["oracle_invocations"][-1] if oracle_fired else None

        return {
            "success": True,
            "newstate": new_state.to_dict(),
            "applied_modes": applied_modes,
            "mv_results": mvresults,              # ← KEY has underscore
            "mv_success_rate": mvsuccessrate,     # ← KEY has underscores
            "threshold_breach": mvsuccessrate < 0.3,  # ← KEY has underscore
            "oracle_fired": oracle_fired,         # ← KEY has underscore
            "oracle_result": oracle_result,       # ← KEY has underscore
        }


    elif tool_name == "pctm_get_mv_diagnostics":
        state_dict = args.get("state", {})
        state = DimensionalState.from_dict(state_dict)
        lossthreshold = args.get("lossthreshold", 0.5)
        stabilitythreshold = args.get("stabilitythreshold", 0.5)
        mvresults, descriptors = engine.test_mathematical_valence(
            state, lossthreshold=lossthreshold, stabilitythreshold=stabilitythreshold
        )
        return {
            "success": True,
            "mvresults": mvresults,
            "descriptors": descriptors,
            "totalorders": len(mvresults),
            "passingorders": len(descriptors),
        }
    elif tool_name == "pctm_test_revision":
        state_dict = args.get("state", {})
        state = DimensionalState.from_dict(state_dict)
        uc_revisions = args.get("uc_revisions")
        md_revisions = args.get("md_revisions")

        # Get baseline MV before any modifications
        baseline_mv_results, baseline_descriptors = engine.test_mathematical_valence(state)
        baseline_success = sum(1 for r in baseline_mv_results.values() if r.get("mv", 0) == 1.0)
        baseline_rate = baseline_success / len(baseline_mv_results) if baseline_mv_results else 0.0

        # Store original canon state
        original_ucs = engine.universal_characteristics[:]
        original_mds = engine.modal_dynamics[:]
        original_W = engine.W.copy()

        try:
            # Apply UC revisions if provided
            if uc_revisions:
                for uc_name, uc_changes in uc_revisions.items():
                    # Find the UC by name
                    for i, uc in enumerate(engine.universal_characteristics):
                        if uc.name.lower() == uc_name.lower():
                            # Modify calculation function if equation changed
                            if "equation" in uc_changes:
                                # Keep original metadata, just update what's in uc_changes
                                for key, value in uc_changes.items():
                                    setattr(uc, key, value)
                            break

            # Apply MD revisions if provided
            if md_revisions:
                for md_name, md_changes in md_revisions.items():
                    # Find the MD by name
                    for i, md in enumerate(engine.modal_dynamics):
                        if md.name.lower() == md_name.lower():
                            # Update MD properties
                            for key, value in md_changes.items():
                                if key != "apply_function":  # Don't try to set function from JSON
                                    setattr(md, key, value)
                            break

            # Recalculate weight matrix if needed
            if uc_revisions or md_revisions:
                engine.W = engine.derive_weight_matrix()

            # Test MV with revised canons
            revised_mv_results, revised_descriptors = engine.test_mathematical_valence(state)
            revised_success = sum(1 for r in revised_mv_results.values() if r.get("mv", 0) == 1.0)
            revised_rate = revised_success / len(revised_mv_results) if revised_mv_results else 0.0

            improvement_delta = revised_rate - baseline_rate
            would_improve = improvement_delta > 0.0

            return {
                "success": True,
                "would_improve_mv": would_improve,
                "baseline_mv_rate": baseline_rate,
                "revised_mv_rate": revised_rate,
                "improvement_delta": improvement_delta,
                "baseline_passing_orders": baseline_success,
                "revised_passing_orders": revised_success,
                "total_orders": len(baseline_mv_results),
            }

        finally:
            # ALWAYS restore original canon state (transient test only)
            engine.universal_characteristics = original_ucs
            engine.modal_dynamics = original_mds
            engine.W = original_W

    else:
        return {"success": False, "error": f"Unknown PCTM tool: {tool_name}"}



def _call_oracle_tool(tool_name: str, args: Dict) -> Dict:
    """
    DEV MODE: Call I Ching oracle directly instead of via MCP subprocess.
    """
    if "iching" in tool_name.lower() or tool_name == "iching_cast":
        try:
            result = ichiRan.iching_cast()
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": f"Unknown oracle tool: {tool_name}"}



@app.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Dynamically expose resources based on current state."""
    global _session

    if _session is None:
        return []

    resources = []

    # Always expose output log
    resources.append(types.Resource(
        uri=f"file:///{_work_dir}/output.json",
        name="Audit Log",
        description="Append-only log of all orchestrator events",
        mimeType="application/json"
    ))

    if _session.state == OrchestratorState.INIT:
        resources.extend([
            types.Resource(
                uri=f"file:///{_work_dir}/UCCanon.json",
                name="Universal Characteristics Canon (read-only)",
                mimeType="application/json"
            ),
            types.Resource(
                uri=f"file:///{_work_dir}/input.json",
                name="Initial Dimensional State (read-write)",
                mimeType="application/json"
            ),
        ])

    elif _session.state == OrchestratorState.ORACLE_CONSULT:
        resources.extend([
            types.Resource(
                uri=f"file:///{_work_dir}/UCCanon.json",
                name="Universal Characteristics Canon (read-only)",
                mimeType="application/json"
            ),
            types.Resource(
                uri=f"file:///{_work_dir}/MDCanon.json",
                name="Modal Dynamics Canon (read-only)",
                mimeType="application/json"
            ),
            types.Resource(
                uri=f"file:///{_work_dir}/oracle_result.json",
                name="Oracle Consultation Result (read-only)",
                mimeType="application/json"
            ),
            types.Resource(
                uri=f"file:///{_work_dir}/revision.json",
                name="Proposed Revision (write)",
                mimeType="application/json"
            ),
        ])

    return resources

@app.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str:
    """Read resource content."""
    from urllib.parse import urlparse
    parsed = urlparse(str(uri))  # Convert AnyUrl to string
    filepath = Path(parsed.path)

    if not filepath.exists():
        raise ValueError(f"Resource not found: {uri}")

    with open(filepath, 'r') as f:
        return f.read()
@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Expose orchestration tools (state-aware)."""
    return [
        types.Tool(
            name="orch_init_session",
            description="Initialize new PCTM orchestration session with dimensional state vector",
            inputSchema={
                "type": "object",
                "properties": {
                    "initial_state": {
                        "type": "object",
                        "description": "Dimensional state vector {vec, rho, tape, order, scale}"
                    },
                    "session_id": {"type": "string", "description": "Optional session ID"},
                },
                "required": ["initial_state"]
            }
        ),
        types.Tool(
            name="orch_execute_step",
            description="Execute PCTM step and monitor for oracle trigger condition",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID from orch_init_session"},
                    "max_steps": {"type": "integer", "default": 1},
                },
                "required": ["session_id"],
            }
        ),
        types.Tool(
            name="orch_consult_oracle",
            description="Manually trigger oracle consultation (or auto-triggered on MV breach)",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "string", "description": "Contextual information for oracle"},
                },
            }
        ),
        types.Tool(
            name="orch_apply_revision",
            description="Apply LLM-proposed UC/MD revision after oracle guidance",
            inputSchema={
                "type": "object",
                "properties": {
                    "revision": {
                        "type": "object",
                        "description": "Revision specification with uc_changes and/or md_changes"
                    },
                    "apply_permanent": {"type": "boolean", "default": False},
                },
                "required": ["revision"]
            }
        ),
        types.Tool(
            name="orch_get_session_state",
            description="Get current session state and context",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle orchestration tool calls."""
    global _session

    arguments = arguments or {}

    if name == "orch_init_session":
        session_id = arguments.get("session_id", f"session_{datetime.utcnow().timestamp()}")
        initial_state = arguments["initial_state"]

        _session = SessionContext(
            session_id=session_id,
            state=OrchestratorState.INIT,
            current_dimensional_state=initial_state,
        )

        # Write initial state to input.json
        with open(_work_dir / "input.json", 'w') as f:
            json.dump(initial_state, f, indent=2)

        _log_to_output({
            "event": "session_init",
            "session_id": session_id,
            "initial_state": initial_state,
        })

        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "session_initialized",
                "session_id": session_id,
                "state": "INIT",
                "resources_available": ["UCCanon.json (r--)", "input.json (rw-)"],
            }, indent=2)
        )]

    elif name == "orch_execute_step":
        if _session is None:
            raise ValueError("No active session. Call orch_init_session first.")

        _session.state = OrchestratorState.COMPUTE

        # Call PCTM to execute step
        pctm_result = _call_pctm_tool("pctm_compute_step", {
            "state": _session.current_dimensional_state,
        })

        # Update session state
        _session.current_dimensional_state = pctm_result["newstate"]
        _session.mv_history.append(pctm_result["mv_results"])

        _log_to_output({
            "event": "pctm_step_executed",
            "session_id": _session.session_id,
            "applied_modes": pctm_result["applied_modes"],
            "mv_success_rate": pctm_result["mv_success_rate"],
            "threshold_breach": pctm_result["threshold_breach"],
        })

        response = {
            "status": "step_complete",
            "new_state": pctm_result["newstate"],
            "mv_success_rate": pctm_result["mv_success_rate"],
        }

        # Check for oracle trigger
        if pctm_result["threshold_breach"]:
            _session.state = OrchestratorState.ORACLE_CONSULT

            # Auto-trigger oracle
            oracle_result = _call_oracle_tool("iching_cast_mcp_iching", {})

            # Save oracle result
            with open(_work_dir / "oracle_result.json", 'w') as f:
                json.dump(oracle_result, f, indent=2)

            _session.oracle_consultations.append(oracle_result)

            _log_to_output({
                "event": "oracle_triggered",
                "session_id": _session.session_id,
                "reason": "mv_threshold_breach",
                "oracle_result": oracle_result,
            })

            response.update({
                "oracle_triggered": True,
                "oracle_result": oracle_result,
                "state_transition": "COMPUTE -> ORACLE_CONSULT",
                "resources_now_available": [
                    "UCCanon.json (r--)",
                    "MDCanon.json (r--)",
                    "oracle_result.json (r--)",
                    "revision.json (-w-)"
                ],
                "next_action": "Interpret oracle guidance and propose revision via orch_apply_revision"
            })

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    elif name == "orch_consult_oracle":
        if _session is None:
            raise ValueError("No active session.")

        _session.state = OrchestratorState.ORACLE_CONSULT

        oracle_result = _call_oracle_tool("iching_cast_mcp_iching", {})

        with open(_work_dir / "oracle_result.json", 'w') as f:
            json.dump(oracle_result, f, indent=2)

        _session.oracle_consultations.append(oracle_result)

        _log_to_output({
            "event": "oracle_consultation",
            "session_id": _session.session_id,
            "trigger": "manual",
            "oracle_result": oracle_result,
        })

        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "oracle_consulted",
                "oracle_result": oracle_result,
                "resources_available": [
                    "UCCanon.json (r--)",
                    "MDCanon.json (r--)",
                    "oracle_result.json (r--)",
                    "revision.json (-w-)"
                ],
            }, indent=2)
        )]

    elif name == "orch_apply_revision":
        if _session is None or _session.state != OrchestratorState.ORACLE_CONSULT:
            raise ValueError("Must be in ORACLE_CONSULT state to apply revision.")

        revision = arguments["revision"]
        apply_permanent = arguments.get("apply_permanent", False)

        if apply_permanent:
            # Test revision first
            test_result = _call_pctm_tool("pctm_test_revision", {
                "state": _session.current_dimensional_state,
                "uc_revisions": revision.get("uc_changes"),
                "md_revisions": revision.get("md_changes"),
            })

            if test_result.get("would_improve_mv"):
                _session.revisions_applied.append(revision)
                _session.state = OrchestratorState.COMPUTE

                _log_to_output({
                    "event": "revision_applied",
                    "session_id": _session.session_id,
                    "revision": revision,
                    "test_results": test_result,
                })

                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "revision_applied_to_session",
                        "would_improve_mv": True,
                        "improvement_delta": test_result.get("improvement_delta"),
                        "state_transition": "ORACLE_CONSULT -> COMPUTE",
                    }, indent=2)
                )]

        # Otherwise just test without applying
        _log_to_output({
            "event": "revision_tested",
            "session_id": _session.session_id,
            "revision": revision,
            "permanent": False,
        })

        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "revision_tested_only",
                "use_apply_permanent_true_to_commit": True,
            }, indent=2)
        )]

    elif name == "orch_get_session_state":
        if _session is None:
            return [types.TextContent(
                type="text",
                text=json.dumps({"status": "no_active_session"}, indent=2)
            )]

        return [types.TextContent(
            type="text",
            text=json.dumps(asdict(_session), indent=2)
        )]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="state-orchestrator-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
