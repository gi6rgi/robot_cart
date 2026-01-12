SHELL := /bin/sh

SNIPPET := boot_config_snippet.txt

.PHONY: configure install

configure:
	@set -e; \
	if [ -f /boot/firmware/config.txt ]; then \
		TARGET=/boot/firmware/config.txt; \
	elif [ -f /boot/config.txt ]; then \
		TARGET=/boot/config.txt; \
	else \
		echo "ERROR: config.txt not found in /boot/firmware/ or /boot/"; exit 1; \
	fi; \
	if [ ! -f "$(SNIPPET)" ]; then \
		echo "ERROR: snippet file not found: $(SNIPPET)"; exit 1; \
	fi; \
	echo "Patching $$TARGET with $(SNIPPET)"; \
	sudo sh -c 'printf "\n" >> "$$0"; cat "$(SNIPPET)" >> "$$0"' "$$TARGET"; \
	echo "Done. Reboot may be required: sudo reboot"

install:
	@set -e; \
	echo "Installing system deps (apt)..."; \
	sudo apt update; \
	sudo apt install -y --no-install-recommends \
		ca-certificates curl \
		python3 python3-venv python3-pip \
		python3-picamera2 python3-opencv python3-numpy \
		pigpio python3-pigpio; \
	if ! command -v uv >/dev/null 2>&1; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH="$$HOME/.local/bin:$$PATH"; \
	fi; \
	echo "Creating venv with system site-packages..."; \
	uv venv --system-site-packages; \
	echo "Installing python deps from pyproject.toml..."; \
	uv sync; \
	echo "Done."
