from ui_metrics import config
from ui_metrics.cli import main, watch_main


def test_native_and_flatpak_defaults(monkeypatch):
    monkeypatch.delenv('OE_METRICS_SOCKET', raising=False)
    monkeypatch.delenv('FLATPAK_ID', raising=False)
    assert str(config.default_socket_path()) == '/tmp/kernel-metrics.sock'
    monkeypatch.setenv('FLATPAK_ID', config.APP_ID)
    monkeypatch.setenv('XDG_RUNTIME_DIR', '/run/user/1000')
    assert str(config.default_socket_path()) == '/run/user/1000/orbital-engineer/metrics.sock'
    monkeypatch.setenv('OE_METRICS_SOCKET', '/tmp/custom.sock')
    assert str(config.default_socket_path()) == '/tmp/custom.sock'


def test_cli_prints_socket_without_gtk(capsys):
    for entrypoint in (main, watch_main):
        assert entrypoint(['--socket', '/tmp/test.sock', '--print-socket-path']) == 0
        assert capsys.readouterr().out.strip() == '/tmp/test.sock'
