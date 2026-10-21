"""Time-windowed metric histories, independent of GTK and Matplotlib."""
from collections import defaultdict, deque
import math

from . import config


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


class MetricsHistory:
    def __init__(self):
        self.durations = defaultdict(deque)
        self.metric_series = {}
        self.history_seconds = {
            "gpu_utilization": config.UTILIZATION_HISTORY_SECONDS,
            "cpu_utilization": config.UTILIZATION_HISTORY_SECONDS,
            "gpu_temperature": config.GPU_TEMPERATURE_HISTORY_SECONDS,
            "energy_error": config.ENERGY_HISTORY_SECONDS,
            "total_KE": config.ENERGY_HISTORY_SECONDS,
            "total_GPE": config.ENERGY_HISTORY_SECONDS,
            "dt_step": config.DT_STEP_HISTORY_SECONDS,
            "num_steps": config.NUM_STEPS_HISTORY_SECONDS,
            "virial_ratio": config.VIRIAL_RATIO_HISTORY_SECONDS,
        }
        self.generation = 0
        self.last_tick = None
        self.last_sim_time = None

    def clear(self):
        self.durations.clear()
        self.metric_series.clear()
        self.last_tick = self.last_sim_time = None
        self.generation += 1

    def consume(self, metric):
        if metric.get("name", "tick") != "tick":
            return False
        tick = metric.get("value")
        sim_time = metric.get("sim_time")
        if not numeric(tick) or not numeric(sim_time):
            return False
        if (tick == 0 or (self.last_tick is not None and tick < self.last_tick)
                or (self.last_sim_time is not None and sim_time < self.last_sim_time)):
            self.clear()
        self.last_tick, self.last_sim_time = tick, sim_time
        for name in self.history_seconds:
            value = metric.get(name)
            if numeric(value):
                self.metric_series.setdefault(name, deque()).append((tick, sim_time, value))
        timeline = metric.get("timeline", [])
        if isinstance(timeline, list):
            for sample in timeline:
                if not isinstance(sample, dict):
                    continue
                name, value = sample.get("name"), sample.get("duration_ms")
                if isinstance(name, str) and numeric(value):
                    self.durations[name].append((tick, sim_time, value))
        for history in (self.durations, self.metric_series):
            for name in list(history):
                seconds = (config.DURATION_HISTORY_SECONDS if history is self.durations
                           else self.history_seconds[name])
                samples = history[name]
                while samples and samples[0][1] < sim_time - seconds:
                    samples.popleft()
                if not samples:
                    del history[name]
        return True
