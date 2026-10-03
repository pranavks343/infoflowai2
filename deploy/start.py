"""Run the internal API and public Streamlit server together."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY in your hosting environment.")
    Path(os.environ.get("DATA_DIR", "/var/data")).mkdir(parents=True, exist_ok=True)
    processes = []

    def stop(signum, frame):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        backend = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=ROOT / "backend",
        )
        processes.append(backend)
        deadline = time.monotonic() + 60
        while True:
            if backend.poll() is not None:
                raise SystemExit("Backend exited during startup.")
            try:
                with urlopen("http://127.0.0.1:8000/openapi.json", timeout=2):
                    break
            except OSError:
                if time.monotonic() >= deadline:
                    raise SystemExit("Backend startup timed out.")
                time.sleep(0.5)
        processes.append(subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "home.py",
             "--server.address", "0.0.0.0", "--server.port", os.getenv("PORT", "10000"),
             "--server.headless", "true", "--browser.gatherUsageStats", "false"],
            cwd=ROOT / "frontend",
        ))
        while all(process.poll() is None for process in processes):
            time.sleep(1)
        raise SystemExit("An application service stopped unexpectedly.")
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    main()
