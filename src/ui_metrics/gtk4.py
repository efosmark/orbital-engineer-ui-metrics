"""The GTK namespaces used by the monitor (no libadwaita dependency)."""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib  # type: ignore
