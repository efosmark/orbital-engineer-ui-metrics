import os
from pathlib import Path

APP_ID = "com.qmew.OrbitalEngineer.Metrics"

WINDOW_TITLE = "Metrics Monitor"

# Native and Flatpak installations share the producer's default socket path.
def default_socket_path():
    override = os.environ.get("OE_METRICS_SOCKET")
    if override:
        return Path(override).expanduser()
    return Path("/tmp/kernel-metrics.sock")

WINDOW_DEFAULT_SIZE = (1200, 1000)

MAX_METRICS_PER_POLL = 500

REFRESH_INTERVAL_MS = 250

# Retain all samples within this many seconds of the latest simulation time.
UTILIZATION_HISTORY_SECONDS = 10
GPU_TEMPERATURE_HISTORY_SECONDS = 10
DURATION_HISTORY_SECONDS = 10
DT_STEP_HISTORY_SECONDS = 10
NUM_STEPS_HISTORY_SECONDS = 10

ENERGY_HISTORY_SECONDS = 180
VIRIAL_RATIO_HISTORY_SECONDS = 180
