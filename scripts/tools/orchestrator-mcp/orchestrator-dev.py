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
    - UCCanon.json: r-- (reference)
    - input.json: rw- (LLM provides initial state)

  ORACLE_CONSULT:
    - UCCanon.json: r-- (reference)
    - MDCanon.json: r-- (reference)
    - oracle_result.json: r-- (oracle output)
    - revision.json: -w- (LLM writes proposed changes)

  REVISION:
    - revision.json: r-- (read proposed changes)
    - UCCanon.json: rw- (apply if approved)
    - MDCanon.json: rw- (apply if approved)

  ALL STATES:
    - output.json: -w- (append-only audit log)
"""

import json
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
sys.path.insert(0, str(Path(__file__).parent.parent / "PCTM-mcp"))
sys.path.insert(0, str(Path(__file__).parent.parent / "iching-mcp"))

from PCTM import PCTMEngine, DimensionalState
import ichiRan

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
            ucpath="UCCanon.json",
            mdpath="MDCanon.json",
            orderspath="OrdersMathematicalSubstrate.json",
            oracleenabled=True,
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

        mvresults = engine.history["mvresults"][-1] if engine.history["mvresults"] else {}
        successes = sum(1 for r in mvresults.values() if r.get("mv", 0) == 1.0)
        total = len(mvresults) if mvresults else 1
        mvsuccessrate = successes / total

        oracle_fired = bool(engine.history["oracleinvocations"])
        oracleresult = engine.history["oracleinvocations"][-1] if oracle_fired else None

        return {
            "success": True,
            "newstate": new_state.to_dict(),
            "appliedmodes": applied_modes,
            "mvresults": mvresults,
            "mvsuccessrate": mvsuccessrate,
            "thresholdbreach": mvsuccessrate < engine.oraclethreshold,
            "oraclefired": oracle_fired,
            "oracleresult": oracleresult,
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
                    "max_steps": {"type": "integer", "default": 1},
                },
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
        _session.current_dimensional_state = pctm_result["new_state"]
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
            "new_state": pctm_result["new_state"],
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

        # Save revision
        with open(_work_dir / "revision.json", 'w') as f:
            json.dump(revision, f, indent=2)

        if apply_permanent:
            # Test revision first
            test_result = _call_pctm_tool("pctm_test_revision", {
                "state": _session.current_dimensional_state,
                "uc_revisions": revision.get("uc_changes"),
                "md_revisions": revision.get("md_changes"),
            })

            if test_result.get("would_improve_mv"):
                # Apply to canons
                if "uc_changes" in revision:
                    with open(_work_dir / "UCCanon.json", 'r+') as f:
                        canon = json.load(f)
                        canon.update(revision["uc_changes"])
                        f.seek(0)
                        json.dump(canon, f, indent=2)
                        f.truncate()

                if "md_changes" in revision:
                    with open(_work_dir / "MDCanon.json", 'r+') as f:
                        canon = json.load(f)
                        canon.update(revision["md_changes"])
                        f.seek(0)
                        json.dump(canon, f, indent=2)
                        f.truncate()

                _session.revisions_applied.append(revision)
                _session.state = OrchestratorState.COMPUTE

                _log_to_output({
                    "event": "revision_applied",
                    "session_id": _session.session_id,
                    "revision": revision,
                    "permanent": True,
                })

                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "revision_applied",
                        "would_improve_mv": True,
                        "state_transition": "ORACLE_CONSULT -> COMPUTE",
                    }, indent=2)
                )]

        # Otherwise just test
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
