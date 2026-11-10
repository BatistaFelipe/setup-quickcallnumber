# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python CLI that updates the "quick call number" on Hikvision ISAPI intercom
devices. For firmware-updated DS-K1T673DX-BR and DS-K1T671MF-L readers each
device needs three sequential ISAPI calls (SIP param → keyCfg → reboot)
before the dial button actually uses the new number.

## Commands

```bash
# Dev install (brings in pytest, pytest-cov, requests-mock, ruff, black, bandit)
pip install -e ".[dev]"

# Run the CLI
setup-intercom --number 3001      # explicit number (choices: 61, 3001)
setup-intercom                    # falls back to QUICK_CALL_NUMBER env var

# Tests — default run (unit only, 100% coverage enforced via --cov-fail-under=100)
pytest

# Tests — single test
pytest tests/key_cfg_test.py::test_put_key_cfg_success -v

# Tests — integration (hits the real device configured in .env)
# --no-cov bypasses the default --cov-fail-under=100 gate, which the
# integration suite alone can't satisfy.
pytest -m integration --no-cov

# Lint, format, security
ruff check src tests
ruff format src tests
black src tests
bandit -r src
```

## Architecture

The script iterates `INTERCOM_PORTS` (CSV) over a single `INTERCOM_HOST` and
runs three ISAPI calls per device in strict order. If any step fails, the
remaining steps for that device are skipped but the loop continues to the
next port — devices stay isolated.

```text
set_quick_call_number()  →  for each port:
    put_sip_params()           # /ISAPI/System/Network/SIP/StandardSipParam  (JSON)
    put_key_cfg()              # /ISAPI/VideoIntercom/keyCfg/1               (XML)
    reboot_device()            # /ISAPI/System/reboot                        (no body)
```

Key design decisions:

- **Cascade abort per device** (`src/sip_params.py` → `set_quick_call_number`):
  a failed SIP or keyCfg call skips the remaining steps for that port so a
  device is never rebooted in an inconsistent state.
- **Shared HTTP session** (`src/utils/http.py`): one module-level
  `requests.Session` reused by SIP, keyCfg and reboot clients.
  `REQUEST_TIMEOUT_SECONDS = 15`, `REBOOT_TIMEOUT_SECONDS = 10`.
- **Reboot timeout treated as success** (`src/reboot.py` → `reboot_device`):
  a `ConnectionError` or `Timeout` after sending the PUT is treated as
  success, because the device has already started rebooting and cannot reply.
- **XML split** (`src/utils/xml_helpers.py`): `defusedxml` for parsing
  untrusted device responses; stdlib `xml.etree` only for building the
  outgoing body (justified inline with `# nosec B405`).
- **Startup env validation** (`src/main.py` → `_require_env`): the CLI exits
  immediately with a clear message if `INTERCOM_HOST`, `INTERCOM_PORTS`,
  `INTERCOM_USER`, `INTERCOM_PASSWORD` — or `QUICK_CALL_NUMBER` when `-n` is
  not passed — are missing or empty.
- **Bilingual logging** (`src/sip_params.py` → `_report_failure`): the one
  message routed to Slack stays in Portuguese for the operators who read the
  channel; all other logs, exception strings, CLI help, and documentation
  are in English.

## Environment

All env vars come from `.env` (loaded by `python-dotenv`):

- Required: `INTERCOM_HOST`, `INTERCOM_PORTS` (CSV), `INTERCOM_USER`, `INTERCOM_PASSWORD`
- Required when `-n`/`--number` is not passed: `QUICK_CALL_NUMBER` (`61` or `3001`)
- Optional: `SLACK_URL` (alert webhook), `LOG_PATH` (default `app.log`)

See `README.md` for the full example.

## Testing

- `pytest` (default) runs unit tests, excludes `@pytest.mark.integration`, and
  fails the build on any coverage regression (`--cov-fail-under=100`).
- Unit tests mock HTTP with `requests-mock` and patch env vars / session
  methods via `monkeypatch`; integration tests under
  `tests/sip_params_test.py::TestClass` require a reachable real device.
- `# pragma: no cover` is reserved for genuinely untestable branches —
  currently only the `if __name__ == "__main__"` guard in `src/main.py`.

## CI

Not configured — there is no `.github/workflows`. Verification runs locally
via the commands above.
