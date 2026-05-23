# Rostek iWMS Printer - PySide6/QML

Python 3.11 rewrite skeleton for the C# `PrintZD421` application.

The target behavior stays close to the original app:

- PySide6/QML desktop UI.
- MVVM structure.
- Local HTTP API for print requests.
- ZPL/PRN template replacement.
- RAW printing through Windows Print Spooler.

## Setup

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```powershell
python -m src.main
```

## Project Shape

- `src/core`: constants, paths, settings, threading helpers.
- `src/models`: request/config/template dataclasses.
- `src/services`: API server, template, print spooler, settings, printer discovery.
- `src/viewmodels`: QML-facing MVVM classes.
- `src/composition`: dependency wiring and QML context binding.
- `src/views/qml`: QML shell, pages, and reusable components.
- `docs`: API contract and migration notes.
