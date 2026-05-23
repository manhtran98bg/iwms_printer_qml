import signal

from src.app import run
try:
    from . import resources_rc  # noqa: F401
except ImportError:
    resources_rc = None


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    raise SystemExit(run())
