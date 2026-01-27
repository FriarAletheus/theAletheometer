#!/usr/bin/env python3
"""
PCTM-mcp/server.py
MCP Server wrapper for PCTMEngine - Pure Computational Core

Exposes PCTM computation via MCP protocol for containerized execution.
Works independently or as subprocess called by StateOrchestrator.
Stdio transport for local dev, HTTP for production Docker.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import mcp.server
import mcp.types as types
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

# Import PCTM engine from toolkit
sys.path.insert(0, str(Path(__file__).parent))
try:
    from PCTM import PCTMEngine, DimensionalState
except ImportError:
    print("ERROR: PCTM.py not found. Ensure toolkit PCTM.py is in same directory.", file=sys.stderr)
    sys.exit(1)

app = mcp.server.Server("pctm-mcp")

# Singleton engine (lazy-loaded)
_engine: Optional[PCTMEngine] = None


def get_engine(
    uc_path: str = "UCCanon.json",
    md_path: str = "MDCanon.json",
    orders_path: str = "Orders_Mathematical_Substrate.json",
    **kwargs
) -> PCTMEngine:
    """Get or create PCTM engine instance."""
    global _engine
    if _engine is None:
        _engine = PCTMEngine(
            uc_path=uc_path,
            md_path=md_path,
            orders_path=orders_path,
            **kwargs
        )
    return _engine


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Expose PCTM computational tools."""
    return [
        types.Tool(
            name="pctm_compute_step",
            description="Execute single PCTM computational step and return MV results, applied modes, and new state",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "DimensionalState as dict with vector, magnitude, tape_id, order"
                    },
                    "uc_path": {
                        "type": "string",
                        "default": "UCCanon.json",
                        "description": "Path to Universal Characteristics canon"
                    },
                    "md_path": {
                        "type": "string",
                        "default": "MDCanon.json",
                        "description": "Path to Modal Dynamics canon"
                    },
                    "oracle_enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable oracle intervention"
                    },
                    "oracle_threshold": {
                        "type": "number",
                        "default": 0.3,
                        "description": "MV success threshold for oracle (0-1)"
                    }
                },
                "required": ["state"]
            }
        ),
        types.Tool(
            name="pctm_get_mv_diagnostics",
            description="Get detailed Mathematical Valence diagnostics for current state across all Orders",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "DimensionalState as dict"
                    },
                    "loss_threshold": {
                        "type": "number",
                        "default": 0.5,
                        "description": "Loss threshold for MV calculation"
                    },
                    "stability_threshold": {
                        "type": "number",
                        "default": 0.5,
                        "description": "Stability threshold for MV calculation"
                    }
                },
                "required": ["state"]
            }
        ),
        types.Tool(
            name="pctm_test_revision",
            description="Test a UC/MD revision without permanently applying it. Returns diagnostics on proposed changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "DimensionalState as dict"
                    },
                    "uc_revisions": {
                        "type": "object",
                        "description": "Modified UC canon (full structure)"
                    },
                    "md_revisions": {
                        "type": "object",
                        "description": "Modified MD canon (full structure)"
                    }
                },
                "required": ["state"]
            }
        ),
        types.Tool(
            name="pctm_get_engine_state",
            description="Retrieve current engine metadata (loaded canons, weight matrix stats, history summary)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any] | None
) -> list[types.TextContent]:
    """Handle tool execution."""
    
    if name == "pctm_compute_step":
        state_dict = arguments.get("state", {})
        try:
            state = DimensionalState.from_dict(state_dict)
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Failed to parse state: {str(e)}"})
            )]
        
        engine = get_engine(
            uc_path=arguments.get("uc_path", "UCCanon.json"),
            md_path=arguments.get("md_path", "MDCanon.json"),
            oracle_enabled=arguments.get("oracle_enabled", True),
            oracle_threshold=arguments.get("oracle_threshold", 0.3)
        )
        
        try:
            applied_modes, new_state = engine.step(state)

            # Safely get MV results - step() appends to history
            mv_results = {}
            if "mv_results" in engine.history and len(engine.history["mv_results"]) > 0:
                mv_results = engine.history["mv_results"][-1]

            # Calculate success rate
            successes = sum(
                1 for order_result in mv_results.values()
                if order_result.get("mv", 0) == 1.0
            )
            total = len(mv_results) if mv_results else 1
            mv_success_rate = successes / total

            # Check if oracle fired
            oracle_fired = False
            oracle_result = None
            if "oracle_invocations" in engine.history and len(engine.history["oracle_invocations"]) > 0:
                oracle_result = engine.history["oracle_invocations"][-1]
                oracle_fired = True

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "new_state": new_state.to_dict(),
                    "applied_modes": applied_modes,
                    "mv_results": mv_results,
                    "mv_success_rate": float(mv_success_rate),
                    "threshold_breach": mv_success_rate < engine.oracle_threshold,
                    "oracle_fired": oracle_fired,
                    "oracle_result": oracle_result
                }, indent=2)
            )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Computation failed: {str(e)}"})
            )]
    
    elif name == "pctm_get_mv_diagnostics":
        state_dict = arguments.get("state", {})
        try:
            state = DimensionalState.from_dict(state_dict)
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Failed to parse state: {str(e)}"})
            )]
        
        engine = get_engine()
        loss_threshold = arguments.get("loss_threshold", 0.5)
        stability_threshold = arguments.get("stability_threshold", 0.5)
        
        try:
            mv_results, descriptors = engine._test_mathematical_valence(
                state,
                loss_threshold=loss_threshold,
                stability_threshold=stability_threshold
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "mv_results": mv_results,
                    "descriptors": descriptors,
                    "total_orders": len(mv_results),
                    "passing_orders": len(descriptors)
                }, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Diagnostics failed: {str(e)}"})
            )]
    
    elif name == "pctm_test_revision":
        state_dict = arguments.get("state", {})
        uc_revisions = arguments.get("uc_revisions")
        md_revisions = arguments.get("md_revisions")
        
        try:
            state = DimensionalState.from_dict(state_dict)
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Failed to parse state: {str(e)}"})
            )]
        
        # Create temporary revised engine
        try:
            if uc_revisions:
                uc_path_temp = "/tmp/UCCanon_revised.json"
                with open(uc_path_temp, 'w') as f:
                    json.dump(uc_revisions, f)
            else:
                uc_path_temp = "UCCanon.json"
            
            if md_revisions:
                md_path_temp = "/tmp/MDCanon_revised.json"
                with open(md_path_temp, 'w') as f:
                    json.dump(md_revisions, f)
            else:
                md_path_temp = "MDCanon.json"
            
            revised_engine = PCTMEngine(uc_path=uc_path_temp, md_path=md_path_temp)
            applied_modes, new_state = revised_engine.step(state)
            
            mv_results_before = get_engine()._test_mathematical_valence(state)[0]
            mv_results_after = revised_engine._test_mathematical_valence(new_state)[0]
            
            successes_before = sum(1 for r in mv_results_before.values() if r.get("mv") == 1.0)
            successes_after = sum(1 for r in mv_results_after.values() if r.get("mv") == 1.0)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "would_improve_mv": successes_after > successes_before,
                    "mv_before": successes_before / len(mv_results_before) if mv_results_before else 0,
                    "mv_after": successes_after / len(mv_results_after) if mv_results_after else 0,
                    "applied_modes": applied_modes,
                    "new_state": new_state.to_dict()
                }, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Revision test failed: {str(e)}"})
            )]
    
    elif name == "pctm_get_engine_state":
        engine = get_engine()
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "n_universal_characteristics": len(engine.universal_characteristics),
                "n_modal_dynamics": len(engine.modal_dynamics),
                "n_orders": len(engine.order_registry.orders),
                "weight_matrix_shape": list(engine.W.shape),
                "weight_matrix_stats": {
                    "min": float(engine.W.min()),
                    "max": float(engine.W.max()),
                    "mean": float(engine.W.mean()),
                    "std": float(engine.W.std()),
                    "sparsity": float((engine.W == 0).sum() / engine.W.size)
                },
                "history_keys": list(engine.history.keys()) if engine.history else [],
                "oracle_enabled": engine.oracle_enabled,
                "oracle_threshold": engine.oracle_threshold,
                "law_mode": engine.law_mode
            }, indent=2)
        )]
    
    return [types.TextContent(
        type="text",
        text=json.dumps({"error": f"Unknown tool: {name}"})
    )]

@app.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Expose PCTM mathematical substrates as resources."""
    resources_dir = Path(__file__).parent.absolute()
    return [
        types.Resource(
            uri=f"file:///{resources_dir.as_posix()}/UCCanon.json",            name="Universal Characteristics Canon",
            description="UC mathematical substrate for dimensional evolution",
            mimeType="application/json"
        ),
        types.Resource(
            uri=f"file:///{resources_dir.as_posix()}/MDCanon.json",            name="Modal Dynamics Canon",
            description="MD operational modes for state transformation",
            mimeType="application/json"
        ),
        types.Resource(
            uri=f"file:///{resources_dir.as_posix()}/Orders_Mathematical_Substrate.json",
            name="Orders Mathematical Substrate",
            description="Ordinal geometry definitions for MV testing across reality Orders (Virtual→Existential)",
            mimeType="application/json"
        ),
    ]

@app.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str:
    """Read resource file content."""
    from urllib.parse import urlparse
    parsed = urlparse(str(uri))
    filepath = Path(parsed.path)

    if not filepath.exists():
        raise ValueError(f"Resource not found: {uri}")

    with open(filepath, 'r') as f:
        return f.read()


async def main():
    """Main entry point for stdio transport."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pctm-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
