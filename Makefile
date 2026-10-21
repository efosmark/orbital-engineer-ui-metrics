.DEFAULT_GOAL := help
PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
APP_ID := com.qmew.OrbitalEngineer.Metrics
MANIFEST := flatpak/$(APP_ID).json
BUILD_DIR := flatpak/build
STATE_DIR := flatpak/.flatpak-builder
ARGS ?=
PYVER_TAG ?= 313
PLAT_TAG ?= manylinux_2_27_x86_64 manylinux_2_28_x86_64 manylinux_2_17_x86_64 manylinux2014_x86_64
WHEELS := flatpak/python3-deps/wheels

.PHONY: help venv install dev run watch test wheel vendor-wheels flatpak-check flatpak-build flatpak-install flatpak-run flatpak-bundle clean distclean
help:
	@echo 'Setup: install dev | Run: run watch (ARGS="--socket PATH")'
	@echo 'Check: test | Package: wheel flatpak-check flatpak-build flatpak-install flatpak-bundle'
	@echo 'Run installed Flatpak: flatpak-run | Cleanup: clean distclean'
venv: $(VENV_PYTHON)
$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)
install: venv
	$(VENV_PYTHON) -m pip install -e .
dev: venv
	$(VENV_PYTHON) -m pip install -e '.[dev]'
run: venv
	$(VENV_PYTHON) -m ui_metrics $(ARGS)
watch: venv
	$(VENV_PYTHON) -c 'from ui_metrics.cli import watch_main; raise SystemExit(watch_main())' $(ARGS)
test: venv
	$(VENV_PYTHON) -m pytest $(ARGS)
wheel: venv
	$(VENV_PYTHON) -m build --wheel --outdir dist
vendor-wheels: venv
	rm -rf $(WHEELS).tmp
	mkdir -p $(WHEELS).tmp
	$(VENV_PYTHON) -m pip download -r flatpak/python3-deps/requirements.txt --dest $(WHEELS).tmp --only-binary=:all: $(foreach platform,$(PLAT_TAG),--platform $(platform)) --implementation cp --python-version $(PYVER_TAG)
	rm -rf $(WHEELS)
	mv $(WHEELS).tmp $(WHEELS)
flatpak-check:
	$(PYTHON) tools/check_flatpak.py
	flatpak-builder --show-manifest $(MANIFEST) > /dev/null
	appstreamcli validate --no-net flatpak/data/$(APP_ID).metainfo.xml
	desktop-file-validate flatpak/data/$(APP_ID).desktop
flatpak-build: flatpak-check vendor-wheels
	flatpak-builder --force-clean --state-dir=$(STATE_DIR) --repo=flatpak/repo $(BUILD_DIR) $(MANIFEST)
flatpak-install: flatpak-build
	flatpak-builder --user --install --export-only --state-dir=$(STATE_DIR) --repo=flatpak/repo $(BUILD_DIR) $(MANIFEST)
flatpak-run:
	flatpak run $(APP_ID) $(ARGS)
flatpak-bundle: flatpak-build
	mkdir -p dist
	flatpak build-bundle flatpak/repo dist/$(APP_ID).flatpak $(APP_ID)
clean:
	rm -rf build dist .pytest_cache src/*.egg-info
distclean: clean
	rm -rf $(WHEELS) $(WHEELS).tmp $(BUILD_DIR) $(STATE_DIR) flatpak/repo
