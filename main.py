import subprocess
import threading

import uvicorn


def run_fastapi() -> None:
    """Run FastAPI in a separate thread."""
    uvicorn.run("src.backend.api.app:app", host="0.0.0.0", port=8000, log_level="info")


def run_streamlit() -> None:
    """Run Streamlit in the foreground."""
    subprocess.run(
        ["streamlit", "run", "src/frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"], check=False
    )


if __name__ == "__main__":
    # Start FastAPI in a daemon thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Run Streamlit in the foreground
    run_streamlit()
