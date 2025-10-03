import sys
import time
from pathlib import Path

# Ensure the project root is on sys.path so test imports like `import app...` work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_sessionstart(session):
    """Create reports dir and store start time."""
    session.config._start_time = time.time()
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)


def pytest_runtest_logreport(report):
    """Print a short per-test summary when each test finishes (call phase)."""
    # only on the call phase (actual test execution)
    if report.when != "call":
        return

    # report.config may not exist on TestReport in some pytest versions; use session.config
    terminal_reporter = None
    try:
        cfg = getattr(report, "config", None)
        if cfg is None and hasattr(report, "session"):
            cfg = getattr(report.session, "config", None)
        if cfg is not None:
            terminal_reporter = cfg.pluginmanager.getplugin("terminalreporter")
    except Exception:
        terminal_reporter = None
    if terminal_reporter is None:
        # fallback to print
        status = "PASSED" if report.passed else ("FAILED" if report.failed else "SKIPPED")
        duration = getattr(report, 'duration', 0.0)
        print(f"> Test {report.nodeid} {status} in {duration:.3f}s")
        return

    status = "PASSED" if report.passed else ("FAILED" if report.failed else "SKIPPED")
    duration = getattr(report, 'duration', 0.0)
    # Use terminal reporter to ensure visibility even with -q
    terminal_reporter.write_line(f"> Test {report.nodeid} {status} in {duration:.3f}s")
