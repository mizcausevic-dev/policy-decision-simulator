from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCALA_CLI = Path(r"C:\Program Files\scala-cli-x86_64-pc-win32\scala-cli.exe")
JAVA_HOME = r"C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot"
PORT = 4514


def get_json(path: str):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}") as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(path: str, payload: dict):
    request = urllib.request.Request(
        f"http://127.0.0.1:{PORT}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    env = os.environ.copy()
    env["JAVA_HOME"] = JAVA_HOME
    env["PATH"] = JAVA_HOME + r"\bin;" + env["PATH"]
    process = subprocess.Popen(
        [str(SCALA_CLI), "run", "src"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(8)
        summary = get_json("/api/dashboard/summary")
        if summary["summary"]["tracked_scenarios"] != 3:
            raise SystemExit("Unexpected scenario count")
        detail = get_json("/api/scenarios/scn-901")
        if detail["risk_band"] != "critical":
            raise SystemExit("Unexpected scenario risk band")
        analysis = post_json(
            "/api/analyze/scenario",
            {
                "risk_band": "critical",
                "dependency_breach_count": 2,
                "change_freeze_active": True,
                "rollback_confidence": 0.41,
                "customer_exposure_pct": 37,
            },
        )
        if analysis["decision"] != "hold":
            raise SystemExit("Unexpected decision")
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
