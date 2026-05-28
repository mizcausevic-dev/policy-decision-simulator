from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORT = 4514

# Resolve scala-cli from PATH (CI extracts it to scala-cli-bin and appends
# that dir to GITHUB_PATH); fall back to a typical Windows install location
# for local dev where the user may have installed it manually.
_SCALA_CLI_FROM_PATH = shutil.which("scala-cli") or shutil.which("scala-cli.exe")
if _SCALA_CLI_FROM_PATH:
    SCALA_CLI = Path(_SCALA_CLI_FROM_PATH)
else:
    SCALA_CLI = Path(r"C:\Program Files\scala-cli-x86_64-pc-win32\scala-cli.exe")

# Honor JAVA_HOME from the environment (setup-java sets it on every runner);
# only fall back to a typical Windows path for local dev.
JAVA_HOME = os.environ.get("JAVA_HOME") or r"C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot"


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
    java_bin = os.path.join(JAVA_HOME, "bin")
    env["PATH"] = java_bin + os.pathsep + env.get("PATH", "")
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
