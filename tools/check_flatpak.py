"""Structural checks that work without flatpak-builder or a graphical session."""
import json
from pathlib import Path
import tomllib
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "flatpak/com.qmew.OrbitalEngineer.Metrics.json").read_text())
app_id = manifest["app-id"]
metadata = ET.parse(root / f"flatpak/data/{app_id}.metainfo.xml").getroot()
assert metadata.findtext("id") == app_id
assert metadata.findtext("launchable") == f"{app_id}.desktop"
desktop = (root / f"flatpak/data/{app_id}.desktop").read_text()
assert f"Icon={app_id}" in desktop
assert (root / f"flatpak/data/{app_id}.svg").is_file()
project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
assert manifest["command"] in project["gui-scripts"]
assert "--filesystem=/tmp" in manifest["finish-args"]
assert "--share=network" not in manifest["finish-args"]
print("Flatpak metadata and entry points are consistent")
