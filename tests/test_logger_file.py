import os
import time

from app.utils.logger import Logger, LOG_DIR


def test_logger_writes_file(tmp_path):
    # The Logger writes to LOG_DIR in the project; ensure a log entry appears there.
    # We'll create a log entry and then check the logs directory for a recent file.
    Logger.info("TEST-LOGGER: starting test entry")
    # Wait briefly to ensure IO flush
    time.sleep(0.1)

    assert os.path.isdir(LOG_DIR)
    files = [os.path.join(LOG_DIR, f) for f in os.listdir(LOG_DIR) if f.startswith("otp-microservice-")]
    assert len(files) > 0
    # pick the most recent file and ensure it's non-empty
    latest = max(files, key=os.path.getmtime)
    assert os.path.getsize(latest) > 0
