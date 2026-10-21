import json
import socket
import pytest
from ui_metrics.transport import MetricSocket


def test_real_datagrams_lock_and_cleanup(tmp_path):
    path = tmp_path / 'runtime' / 'metrics.sock'
    with MetricSocket(path) as receiver:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sender:
            sender.sendto(json.dumps({'value': 1}).encode(), str(path))
            assert receiver.receive() == {'value': 1}
            for data in (b'not json', b'\xff', b'[]'):
                sender.sendto(data, str(path))
                assert receiver.receive() is None
        with pytest.raises(RuntimeError, match='Another metrics reader'):
            MetricSocket(path)
        assert path.exists()
    assert not path.exists()
    # A clean restart can acquire the same endpoint.
    with MetricSocket(path):
        assert path.exists()


def test_stale_socket_and_regular_file(tmp_path):
    path = tmp_path / 'metrics.sock'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(str(path))
    sock.close()
    with MetricSocket(path):
        assert path.exists()
    path.write_text('keep me')
    with pytest.raises(RuntimeError, match='non-socket'):
        MetricSocket(path)
    assert path.read_text() == 'keep me'
