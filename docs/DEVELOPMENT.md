# Development

## Requirements
- Python 3.11+
- pip and a virtual environment
- PySide6 and platformdirs (installed from project metadata)

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m lifeos
```

## Test

```bash
pytest
```

The SQLite database is stored in the operating system's per-user application-data directory. The storage module accepts an explicit path so tests can use a temporary database.
