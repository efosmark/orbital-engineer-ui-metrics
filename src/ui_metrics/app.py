"""GTK application lifecycle and socket polling."""
import sys

from . import config
from .gtk4 import Gtk, Gio, GLib
from .history import MetricsHistory
from .plot import PlotWindow
from .transport import MetricSocket


class MetricsApp(Gtk.Application):
    def __init__(self, socket_path=None):
        super().__init__(application_id=config.APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.socket_path = socket_path or config.default_socket_path()
        self.history = MetricsHistory()
        self.plot_win = None
        self.receiver = None
        self.startup_error = None
        self._refresh_source_id = 0

    def do_startup(self):
        Gtk.Application.do_startup(self)
        try:
            self.receiver = MetricSocket(self.socket_path)
        except (OSError, RuntimeError) as exc:
            self.startup_error = str(exc)
            print(f"Cannot listen for metrics: {exc}", file=sys.stderr)
            self.quit()
            return
        print(f"Listening on {self.socket_path}")
        self._refresh_source_id = GLib.timeout_add(config.REFRESH_INTERVAL_MS, self._periodic_refresh)

    def _periodic_refresh(self):
        if self.receiver is None:
            return True
        received = False
        for _ in range(config.MAX_METRICS_PER_POLL):
            try:
                metric = self.receiver.receive()
            except BlockingIOError:
                break
            if metric is None:
                continue
            generation = self.history.generation
            if self.history.consume(metric):
                received = True
                if self.history.generation != generation and self.plot_win is not None:
                    self.plot_win.reset_plot()
        if received and self.plot_win is not None:
            self.plot_win.queue_redraw()
        return True

    def clear_metrics(self, *, force_redraw=False):
        self.history.clear()
        if self.plot_win is not None:
            self.plot_win.reset_plot(force_redraw=force_redraw)

    def do_activate(self):
        if self.receiver is None:
            return
        if self.plot_win is None:
            self.plot_win = PlotWindow(self, self.history.durations, self.history.metric_series)
            self.plot_win.connect("destroy", self._on_plot_window_destroyed)
        self.plot_win.present()
        self.plot_win.queue_redraw()

    def _on_plot_window_destroyed(self, _window):
        self.plot_win = None

    def do_shutdown(self):
        if self._refresh_source_id:
            GLib.source_remove(self._refresh_source_id)
            self._refresh_source_id = 0
        if self.receiver is not None:
            self.receiver.close()
            self.receiver = None
        Gtk.Application.do_shutdown(self)
