# tap-appstore — Python 3.11 Regression Tests

Runs the real tap against the real App Store Connect API, compares output between 3.9 and 3.11.

## Required env vars

```bash
export TAP_APPSTORE_KEY_ID=848S254RX8
export TAP_APPSTORE_KEY_FILE="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
export TAP_APPSTORE_ISSUER_ID=5c84557a-4920-4e89-91d8-82ba061e2336
export TAP_APPSTORE_VENDOR=91884281
export TAP_APPSTORE_START_DATE=2025-01-01T00:00:00Z  # optional
```

## Usage

```bash
# Capture baseline (master + Python 3.9)
git checkout master
bash test/regression/run_capture.sh

# Run tests (migration branch + Python 3.11)
git checkout python-311-migration
bash test/regression/run_tests.sh
```
