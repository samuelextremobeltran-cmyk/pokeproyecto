#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
jobs="${JOBS:-4}"
mkdir -p project/local
make firered -j"$jobs" 2>&1 | tee project/local/build-firered.log
test -s pokefirered.gba
sha256sum pokefirered.gba | tee project/local/rom.sha256
