#!/usr/bin/env python3
import subprocess, sys

sys.exit(
    subprocess.call(
        [
            sys.executable,
            str(
                __import__("pathlib").Path(__file__).resolve().parent
                / "tools/console.py"
            ),
        ]
        + sys.argv[1:]
    )
)
