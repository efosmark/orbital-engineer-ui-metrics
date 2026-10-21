"""Terminal receiver for the same protocol as the GUI."""
from collections import defaultdict
import select

from .transport import MetricSocket


def watch(path):
    with MetricSocket(path) as receiver:
        print(f"Listening on {path}", flush=True)
        while True:
            select.select([receiver.sock], [], [])
            try:
                metric = receiver.receive()
            except BlockingIOError:
                continue
            if metric is None or metric.get("name", "tick") != "tick":
                continue
            print(f"\nTick {metric.get('value')}  Sim Time {metric.get('sim_time')}")
            durations = defaultdict(list)
            for sample in metric.get("timeline", []):
                if isinstance(sample, dict) and isinstance(sample.get("duration_ms"), (int, float)):
                    durations[str(sample.get("name", "unnamed"))].append(sample["duration_ms"])
            for name, samples in sorted(durations.items(), key=lambda item: sum(item[1]), reverse=True):
                print(f"{name:<36} count={len(samples):<5} avg={sum(samples)/len(samples):.3f} ms")
