from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    # Railway may keep manually configured Streamlit env vars. A literal "$PORT"
    # breaks Streamlit because server.port must be an integer.
    os.environ.pop("STREAMLIT_SERVER_PORT", None)
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"

    port = "8080"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.address=0.0.0.0",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
