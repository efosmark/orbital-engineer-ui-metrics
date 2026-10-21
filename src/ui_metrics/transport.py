"""Own a local metrics socket without stealing another monitor's endpoint."""
import fcntl
import json
import socket
import stat
from pathlib import Path


class MetricSocket:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = self.path.with_name(self.path.name + ".lock").open("a")
        self.sock = None
        self._identity = None
        try:
            try:
                fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RuntimeError(f"Another metrics reader is using {self.path}") from exc
            if self.path.exists() or self.path.is_symlink():
                if self.path.is_symlink() or not stat.S_ISSOCK(self.path.stat().st_mode):
                    raise RuntimeError(f"Refusing to replace a non-socket: {self.path}")
                self.path.unlink()
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.sock.bind(str(self.path))
            info = self.path.stat()
            self._identity = (info.st_dev, info.st_ino)
            self.sock.setblocking(False)
        except BaseException:
            self.close()
            raise

    def receive(self):
        if self.sock is None:
            raise RuntimeError("Metrics socket is closed")
        data = self.sock.recv(65536)
        try:
            metric = json.loads(data)
        except (ValueError, UnicodeDecodeError):
            return None
        return metric if isinstance(metric, dict) else None

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
        if self._identity is not None:
            try:
                info = self.path.stat()
                if (info.st_dev, info.st_ino) == self._identity:
                    self.path.unlink()
            except FileNotFoundError:
                pass
            self._identity = None
        self._lock.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
