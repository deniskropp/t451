#!/usr/bin/env python3
"""
activate_scheduler.py
Concrete, runnable scheduler activation for the Journal-as-Agent MVP (TAS-JAA-001).

This is the "turn the scheduler hints into something you can actually launch" step.

Modes:
  --watch   : Poll the memory path (and optionally the project dir) and re-run the agent on changes.
  --loop    : Simple fixed-interval loop (default 4 hours, configurable).
  --once    : Single run (same as calling the mvp directly).

It always uses the operational path (--once under the hood) and the local journal_state/.

Usage examples:
  # One-shot (safe)
  python3 journal_state/activate_scheduler.py --once

  # Polling watcher (good when no inotify)
  python3 journal_state/activate_scheduler.py --watch --interval 300   # check every 5 min

  # Background it:
  nohup python3 journal_state/activate_scheduler.py --watch --interval 900 > journal_state/scheduler.log 2>&1 &

  # Fixed loop every 4h
  python3 journal_state/activate_scheduler.py --loop --interval 14400

When real memory.md appears at ~/.grok/user_info/memory.md (or you point --memory), changes will trigger full rich cycles.
The scheduler also watches for new demo / sidecar artifacts in demos/ and journal_state/ to encourage re-runs after Parallel_f work etc.

This script itself can be called from cron or launched as a long-lived process on the Berlin Node / any dev machine.
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATE_DIR = os.path.join(PROJECT_ROOT, "journal_state")
MVP_SCRIPT = os.path.join(PROJECT_ROOT, "journal_as_agent_mvp.py")

DEFAULT_MEMORY = os.path.expanduser("~/.grok/user_info/memory.md")
FALLBACK_MEMORIES = [
    DEFAULT_MEMORY,
    "/home/workdir/.grok/user_info/memory.md",
    os.path.join(PROJECT_ROOT, "memory.md"),
]


def find_memory(explicit: str = None) -> str:
    if explicit and os.path.exists(explicit):
        return explicit
    for p in FALLBACK_MEMORIES:
        if os.path.exists(p):
            return p
    return DEFAULT_MEMORY  # will cause bootstrap warning inside the MVP, which is fine


def run_journal_once(memory_path: str):
    print(f"[{datetime.now().isoformat(timespec='seconds')}] Triggering operational journal cycle...")
    cmd = [
        sys.executable,
        MVP_SCRIPT,
        "--once",
        "--state-dir", STATE_DIR,
        "--memory", memory_path,
        "--project-root", PROJECT_ROOT,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[-2000:])
        print(f"[{datetime.now().isoformat(timespec='seconds')}] Cycle finished (return={result.returncode})")
    except Exception as e:
        print(f"ERROR running journal cycle: {e}")


def watch_loop(memory_path: str, interval: int, also_watch_dirs: list):
    print(f"Starting watch mode. Polling every {interval}s.")
    print(f"  Memory: {memory_path}")
    print(f"  Extra watch dirs: {also_watch_dirs}")
    last_mtime = {}
    paths_to_watch = [memory_path] + [p for p in also_watch_dirs if os.path.exists(p)]

    for p in paths_to_watch:
        try:
            last_mtime[p] = os.path.getmtime(p) if os.path.isfile(p) else os.stat(p).st_mtime
        except Exception:
            last_mtime[p] = 0

    while True:
        changed = False
        for p in list(last_mtime.keys()):
            try:
                current = os.path.getmtime(p) if os.path.isfile(p) else os.stat(p).st_mtime
                if current > last_mtime[p]:
                    print(f"  Detected change in {p}")
                    last_mtime[p] = current
                    changed = True
            except FileNotFoundError:
                pass

        if changed or not last_mtime:  # first iteration or explicit
            run_journal_once(memory_path)

        time.sleep(interval)


def fixed_loop(memory_path: str, interval: int):
    print(f"Starting fixed-interval loop every {interval}s (~{interval/3600:.1f}h).")
    while True:
        run_journal_once(memory_path)
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Journal-as-Agent scheduler activator")
    parser.add_argument("--memory", default=None, help="Explicit memory.md path")
    parser.add_argument("--once", action="store_true", help="Run exactly one operational cycle then exit")
    parser.add_argument("--watch", action="store_true", help="Poll for changes and re-run on memory / artifact updates")
    parser.add_argument("--loop", action="store_true", help="Fixed interval loop (no change detection)")
    parser.add_argument("--interval", type=int, default=14400, help="Seconds between runs (default 4h = 14400)")
    parser.add_argument("--watch-dirs", nargs="*", default=["demos", "journal_state"], help="Additional directories to poll for changes")
    args = parser.parse_args()

    memory_path = find_memory(args.memory)

    if args.once:
        run_journal_once(memory_path)
        return

    watch_paths = [os.path.join(PROJECT_ROOT, d) for d in args.watch_dirs]

    if args.watch:
        watch_loop(memory_path, max(30, args.interval), watch_paths)
    elif args.loop:
        fixed_loop(memory_path, max(60, args.interval))
    else:
        print("No mode selected. Use --once, --watch, or --loop. See --help.")
        parser.print_help()


if __name__ == "__main__":
    main()
