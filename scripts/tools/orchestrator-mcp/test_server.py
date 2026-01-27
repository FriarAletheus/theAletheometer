#!/usr/bin/env python3
import sys
sys.path.insert(0, str(__file__).replace('/test_orchestrator.py', ''))
sys.path.insert(0, '../PCTM-mcp')
sys.path.insert(0, '../iching-mcp')

from orchestrator import app, _call_pctm_tool
import json

# Test PCTM engine loads
print("Testing PCTM tool call...")
try:
    result = _call_pctm_tool("pctm_get_engine_state", {})
    print("✓ PCTM engine loaded successfully")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"✗ PCTM error: {e}")
    import traceback
    traceback.print_exc()
