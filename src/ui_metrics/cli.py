"""Command-line entry points; --help works without a graphical session."""
import argparse
from pathlib import Path

from . import __version__, config


def parser(description):
    result = argparse.ArgumentParser(description=description)
    result.add_argument("--version", action="version", version=__version__)
    result.add_argument("--socket", type=Path, default=config.default_socket_path(),
                        help="Unix datagram socket path (or set OE_METRICS_SOCKET)")
    result.add_argument("--print-socket-path", action="store_true",
                        help="Print the resolved socket path and exit")
    return result


def main(argv=None):
    args = parser("Display live Orbital Engineer metrics").parse_args(argv)
    if args.print_socket_path:
        print(args.socket)
        return 0
    from .app import MetricsApp
    app = MetricsApp(args.socket.expanduser())
    result = app.run([])
    return 1 if app.startup_error else result


def watch_main(argv=None):
    args = parser("Print Orbital Engineer timing metrics").parse_args(argv)
    if args.print_socket_path:
        print(args.socket)
        return 0
    from .watch import watch
    try:
        watch(args.socket.expanduser())
    except KeyboardInterrupt:
        pass
    return 0
