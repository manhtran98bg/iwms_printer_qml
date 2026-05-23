# Project Structure

```text
printer_pyside6_qml/
  docs/
  scripts/
  tests/
  src/
    app.py
    main.py
    core/
    models/
    services/
    viewmodels/
    composition/
    views/qml/
```

The structure follows the MESLink reference project:

- `ApplicationContainer` owns service and ViewModel creation.
- `qml_context.py` exposes ViewModels to QML.
- Services stay independent from QML.
- ViewModels expose `Property`, `Signal`, and `Slot` APIs only.
