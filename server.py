#!/usr/bin/env python3
"""
POD Smart Router - Sovereign Entrypoint & Daemon
Port 8117
"""
import sys
import os
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from pod_smart_router.server import run_server, PORT

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="POD Smart Router Daemon")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on (default 8117)")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
