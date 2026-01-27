from fastmcp import FastMCP
import os
from pathlib import Path

mcp = FastMCP("OntologiesFS")

ROOT = Path(os.environ.get("PROJECT_ROOT", "/data")).resolve()

def safe_path(p: str) -> Path:
    target = (ROOT / p).resolve()
    if not str(target).startswith(str(ROOT)):
        raise ValueError("Path escapes PROJECT_ROOT")
    return target

@mcp.tool()
def list_files(rel_dir: str = "."):
    d = safe_path(rel_dir)
    return sorted([p.name for p in d.iterdir()])

@mcp.tool()
def read_file(rel_path: str):
    p = safe_path(rel_path)
    return p.read_text(encoding="utf-8", errors="replace")

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=3000, path="/mcp")
