#!/usr/bin/env python3
"""
Baseline capture for tap-appstore — run once on Python 3.9.

Runs the REAL tap against the REAL App Store Connect API.

Required env vars:
    TAP_APPSTORE_KEY_ID
    TAP_APPSTORE_KEY_FILE       (PEM private key content, with literal \\n)
    TAP_APPSTORE_ISSUER_ID
    TAP_APPSTORE_VENDOR
    TAP_APPSTORE_START_DATE     (optional, default 2025-01-01T00:00:00Z)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BASELINE_DIR = Path(__file__).parent / "baseline"
TAP_CMD = str(Path(sys.executable).parent / "tap-appstore")

REQUIRED = [
    "TAP_APPSTORE_KEY_ID",
    "TAP_APPSTORE_KEY_FILE",
    "TAP_APPSTORE_ISSUER_ID",
    "TAP_APPSTORE_VENDOR",
]


def check_env():
    missing = [v for v in REQUIRED if not os.getenv(v)]
    if missing:
        print(f"ERROR: Missing env vars: {missing}")
        sys.exit(1)


def write_config():
    config = {
        "key_id": os.environ["TAP_APPSTORE_KEY_ID"],
        "key_file": os.environ["TAP_APPSTORE_KEY_FILE"],
        "issuer_id": os.environ["TAP_APPSTORE_ISSUER_ID"],
        "vendor": os.environ["TAP_APPSTORE_VENDOR"],
        "start_date": os.getenv("TAP_APPSTORE_START_DATE", "2025-01-01T00:00:00Z"),
    }
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(config, tmp)
    tmp.close()
    return tmp.name


def _env():
    env = os.environ.copy()
    env.setdefault("AES_SECRET_KEY", "peliqan-test-key")
    return env


def discover(config_path):
    print("Discovering catalog...")
    result = subprocess.run(
        [TAP_CMD, "--config", config_path, "--discover"],
        capture_output=True, text=True, env=_env()
    )
    if result.returncode != 0:
        print("ERROR: discover failed.")
        print("STDERR:", result.stderr[-2000:])
        sys.exit(1)
    catalog = json.loads(result.stdout)
    print(f"Discovered {len(catalog.get('streams', []))} streams.")
    return catalog


def select_all(catalog):
    for stream in catalog.get("streams", []):
        for entry in stream.get("metadata", []):
            entry.setdefault("metadata", {})["selected"] = True
    return catalog


def write_catalog(catalog):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(catalog, tmp)
    tmp.close()
    return tmp.name


def run_sync(config_path, catalog_path):
    print(f"Syncing with Python {sys.version.split()[0]}...")
    result = subprocess.run(
        [TAP_CMD, "--config", config_path, "--catalog", catalog_path],
        capture_output=True, text=True, env=_env()
    )
    if result.returncode != 0:
        print("WARNING: tap exited non-zero. Capturing partial output.")
        print("STDERR (tail):", result.stderr[-2000:])
    return result.stdout


def parse_output(output):
    schemas, records, states = {}, {}, []
    for line in output.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = msg.get("type")
        if t == "SCHEMA":
            schemas[msg["stream"]] = msg["schema"]
            records.setdefault(msg["stream"], [])
        elif t == "RECORD":
            records.setdefault(msg["stream"], []).append(msg["record"])
        elif t == "STATE":
            states.append(msg["value"])
    return schemas, records, states


def extract_state_keys(states):
    keys = {}
    for state in states:
        for stream, bookmark in state.get("bookmarks", {}).items():
            keys[stream] = sorted(bookmark.keys()) if isinstance(bookmark, dict) else []
    return keys


def extract_record_fields(records):
    fields = {}
    for stream, stream_records in records.items():
        all_fields = set()
        for record in stream_records:
            all_fields.update(record.keys())
        fields[stream] = sorted(all_fields)
    return fields


def main():
    check_env()
    config_path = write_config()
    catalog_path = None

    try:
        catalog = discover(config_path)
        select_all(catalog)
        catalog_path = write_catalog(catalog)

        output = run_sync(config_path, catalog_path)
        schemas, records, states = parse_output(output)

        BASELINE_DIR.mkdir(parents=True, exist_ok=True)

        (BASELINE_DIR / "catalog.json").write_text(
            json.dumps(catalog, indent=2, sort_keys=True)
        )
        (BASELINE_DIR / "schemas.json").write_text(
            json.dumps(schemas, indent=2, sort_keys=True)
        )
        print(f"Saved schemas for {len(schemas)} streams: {list(schemas.keys())}")

        state_keys = extract_state_keys(states)
        (BASELINE_DIR / "state_keys.json").write_text(
            json.dumps(state_keys, indent=2, sort_keys=True)
        )
        print(f"Saved state keys for {len(state_keys)} streams")

        record_fields = extract_record_fields(records)
        (BASELINE_DIR / "record_fields.json").write_text(
            json.dumps(record_fields, indent=2, sort_keys=True)
        )
        total = sum(len(v) for v in records.values())
        print(f"Saved record fields for {len(record_fields)} streams ({total} records total)")

        meta = {"python_version": sys.version.split()[0], "streams": list(schemas.keys())}
        (BASELINE_DIR / "meta.json").write_text(json.dumps(meta, indent=2))

        print(f"\nBaseline captured on Python {sys.version.split()[0]}.")
        print(f"Files written to: {BASELINE_DIR}")

    finally:
        os.unlink(config_path)
        if catalog_path:
            os.unlink(catalog_path)


if __name__ == "__main__":
    main()
