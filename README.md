# Setup Quick Call Number

Python automation to update the quick call number on Hikvision intercom devices
via the ISAPI protocol, using HTTP Digest authentication.

## Features

- **Batch update**: Supports multiple devices configured by port.
- **Full post-firmware update**: For recent-firmware Hikvision readers
  (DS-K1T673DX-BR, DS-K1T671MF-L), the `callNumber` is also updated at
  `/ISAPI/VideoIntercom/keyCfg/1` and the device is automatically rebooted
  after configuration, ensuring the dial button uses the new number.
- **Digest authentication**: Secure integration with the ISAPI protocol.
- **Slack alerts**: Automatic notification on configuration failure
  (operator-facing messages are kept in Portuguese).
- **Flexible CLI**: Accepts the number via command line or environment variable.

## Requirements

- Python >= 3.8
- Intercom device with ISAPI support (e.g., Hikvision)

## Configuration

Create a `.env` file at the project root with the following variables:

```env
INTERCOM_HOST=192.168.1.100
INTERCOM_PORTS=80,81,82
INTERCOM_USER=admin
INTERCOM_PASSWORD=your_password
QUICK_CALL_NUMBER=61
SLACK_URL=https://hooks.slack.com/services/your_webhook
LOG_PATH=app.log
```

All of `INTERCOM_HOST`, `INTERCOM_PORTS`, `INTERCOM_USER`, `INTERCOM_PASSWORD`
are required at startup — missing or empty values cause the CLI to exit with
a clear error. `QUICK_CALL_NUMBER` is only required when `--number` is not
passed on the command line.

## Usage

### 1. Installation

For production:

```bash
pip install .
```

For development (includes `pytest`, `pytest-cov`, `requests-mock`, `ruff`,
`black`, `bandit`):

```bash
pip install -e ".[dev]"
```

### 2. Execution

Using the default value from `.env`:

```bash
setup-intercom
```

Passing a specific number via argument:

```bash
setup-intercom --number 3001
```

## Testing

The project uses `pytest`. Unit tests use `requests-mock`; integration tests
(marked with `@pytest.mark.integration`) hit a real device and are excluded
by default. The default `pytest` invocation also enforces 100% coverage on
`src/` — any regression breaks the build.

Run unit tests (default):

```bash
pytest
```

Run integration tests (requires a reachable real device):

```bash
pytest -m integration
```

Lint, format, and security scan:

```bash
ruff check src tests
black --check src tests
bandit -r src
```

## Project Structure

- `src/main.py`: Application entry point and env var validation.
- `src/sip_params.py`: SIP client (GET/PUT) and per-device orchestration.
- `src/key_cfg.py`: `keyCfg` ISAPI client (dial button configuration).
- `src/reboot.py`: Device reboot ISAPI client.
- `src/utils/helpers.py`: Shared helpers (logging, Slack, auth, CLI, `RequestError`).
- `src/utils/http.py`: Shared `requests.Session` and timeout constants.
- `src/utils/xml_helpers.py`: XML parsing (defusedxml) and serialization.
- `tests/`: Unit tests (mocked) and integration tests (`@pytest.mark.integration`).
- `pyproject.toml`: Dependencies, tool configuration, and metadata.
