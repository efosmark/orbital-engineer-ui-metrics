from ui_metrics import config
from ui_metrics.history import MetricsHistory


def packet(tick, time, **values):
    return {'name': 'tick', 'value': tick, 'sim_time': time, **values}


def test_retains_dense_samples_and_expires_startup_names(monkeypatch):
    monkeypatch.setattr(config, 'DURATION_HISTORY_SECONDS', 1)
    history = MetricsHistory()
    history.history_seconds['gpu_utilization'] = 2
    for i in range(200):
        history.consume(packet(i, i / 1000, gpu_utilization=0,
                               timeline=[{'name': 'startup', 'duration_ms': 2}]))
    assert len(history.durations['startup']) == 200
    assert len(history.metric_series['gpu_utilization']) == 200
    history.consume(packet(200, 1.5))
    assert not history.durations
    assert len(history.metric_series['gpu_utilization']) == 200
    history.consume(packet(201, 3))
    assert not history.metric_series


def test_restart_and_clear_preserve_dictionary_references():
    history = MetricsHistory()
    durations, series = history.durations, history.metric_series
    history.consume(packet(200, 20, energy_error=-1))
    generation = history.generation
    history.consume(packet(2, .1, num_steps=1))
    assert history.generation == generation + 1
    assert set(series) == {'num_steps'}
    history.consume(packet(3, 0, energy_error=0))
    assert set(series) == {'energy_error'}
    history.clear()
    assert not series and not durations
    assert history.metric_series is series and history.durations is durations


def test_malformed_and_unrelated_metrics():
    history = MetricsHistory()
    for metric in ({'name': 'gpu_utilization', 'value': 2}, {'value': 'bad', 'sim_time': 0},
                   {'value': 1, 'sim_time': float('nan')}, {'value': 1}):
        assert not history.consume(metric)
    assert history.consume(packet(1, 0, gpu_temperature=None, num_steps=0,
                                  timeline=[None, {}, {'name': 'valid', 'duration_ms': 1}]))
    assert list(history.metric_series) == ['num_steps']
    assert list(history.durations) == ['valid']
