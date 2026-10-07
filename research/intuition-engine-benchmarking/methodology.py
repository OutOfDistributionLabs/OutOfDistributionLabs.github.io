#!/usr/bin/env python3
"""Project entry point for the reusable benchmark methodology. No trials run here."""
import runpy
import sys
from pathlib import Path
PROJECT=Path(__file__).resolve().parent
if '--protocol' not in sys.argv:
    sys.argv[1:1]=['--protocol',str(PROJECT/'protocol.json')]
runpy.run_path(str(PROJECT.parents[1]/'tools/benchmarking/methodology.py'),run_name='__main__')
