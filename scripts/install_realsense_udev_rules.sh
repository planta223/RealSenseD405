#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RULE_SOURCE="${SCRIPT_DIR}/../config/99-realsense-d405.rules"
RULE_DESTINATION="/etc/udev/rules.d/99-realsense-d405.rules"

if [[ ! -f "${RULE_SOURCE}" ]]; then
    printf 'Rule file not found: %s\n' "${RULE_SOURCE}" >&2
    exit 1
fi

if ! command -v udevadm >/dev/null 2>&1; then
    printf 'udevadm is required but was not found.\n' >&2
    exit 1
fi

printf 'Installing D405 udev rule: %s\n' "${RULE_DESTINATION}"
sudo install -o root -g root -m 0644 \
    "${RULE_SOURCE}" \
    "${RULE_DESTINATION}"

sudo udevadm control --reload-rules
sudo udevadm trigger

printf '%s\n' 'D405 udev rule installed.'
printf '%s\n' 'Unplug and reconnect the camera if it is still not detected.'
printf '%s\n' 'Then verify with:'
printf '%s\n' \
    "  python3 -c 'import pyrealsense2 as rs; print(len(rs.context().query_devices()))'"
