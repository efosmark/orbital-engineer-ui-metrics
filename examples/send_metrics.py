"""Send synthetic metrics to a running monitor; no third-party dependencies."""
import argparse
import json
import math
import socket
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--socket", type=Path, default=Path("/tmp/kernel-metrics.sock"))
parser.add_argument("--ticks", type=int, default=500)
args = parser.parse_args()
with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sender:
    for tick in range(args.ticks):
        phase = tick / 20
        packet = {"name": "tick", "value": tick, "sim_time": tick * 0.1,
                  "gpu_utilization": 40 + 20 * math.sin(phase), "cpu_utilization": 20,
                  "gpu_temperature": 60 + 5 * math.sin(phase), "dt_step": 0.1,
                  "num_steps": 1 + tick % 5, "energy_error": 0.001 * math.sin(phase),
                  "total_KE": 1e8, "total_GPE": -2e8, "virial_ratio": 1 + 0.1 * math.sin(phase),
                  "timeline": [{"name": "synthetic step", "duration_ms": 1 + math.sin(phase) / 2}]}
        sender.sendto(json.dumps(packet).encode(), str(args.socket))
        time.sleep(0.05)
