#!/usr/bin/env bash
set -euo pipefail
TAP_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
echo "==> Running baseline capture in python:3.9-slim"
docker run --rm \
  -v "$TAP_DIR":/tap -w /tap \
  -e TAP_APPSTORE_KEY_ID="${TAP_APPSTORE_KEY_ID:?}" \
  -e TAP_APPSTORE_KEY_FILE="${TAP_APPSTORE_KEY_FILE:?}" \
  -e TAP_APPSTORE_ISSUER_ID="${TAP_APPSTORE_ISSUER_ID:?}" \
  -e TAP_APPSTORE_VENDOR="${TAP_APPSTORE_VENDOR:?}" \
  -e TAP_APPSTORE_START_DATE="${TAP_APPSTORE_START_DATE:-2025-01-01T00:00:00Z}" \
  -e AES_SECRET_KEY="peliqan-test-key" \
  python:3.9-slim \
  bash -c "
    apt-get update -qq && apt-get install -y -qq git > /dev/null
    pip install -e . -q 2>/dev/null
    python test/regression/capture.py
  "
echo "==> Baseline written to test/regression/baseline/"
