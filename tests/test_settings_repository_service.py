from __future__ import annotations

import json

from src.core.constants import DEFAULT_SCHEMA_FILENAME, DEFAULT_TEMPLATE_FILENAME
from src.services import settings_repository_service as settings_module
from src.services.settings_repository_service import SettingsRepositoryService


def test_load_first_run_creates_default_template_files(tmp_path, monkeypatch):
    template_dir = tmp_path / ".dfprinter" / "template"
    config_path = tmp_path / ".dfprinter" / "config.json"
    monkeypatch.setattr(settings_module, "DEFAULT_TEMPLATE_DIR", template_dir)

    config = SettingsRepositoryService(config_path=config_path).load()

    schema_path = template_dir / DEFAULT_SCHEMA_FILENAME
    template_path = template_dir / DEFAULT_TEMPLATE_FILENAME
    assert schema_path.exists()
    assert template_path.exists()
    assert config.data_path == str(schema_path)
    assert config.template_path == str(template_path)

    saved_config = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved_config["data_path"] == str(schema_path)
    assert saved_config["template_path"] == str(template_path)


def test_load_does_not_overwrite_existing_default_files(tmp_path, monkeypatch):
    template_dir = tmp_path / ".dfprinter" / "template"
    template_dir.mkdir(parents=True)
    schema_path = template_dir / DEFAULT_SCHEMA_FILENAME
    schema_path.write_text('{"custom": true}', encoding="utf-8")
    monkeypatch.setattr(settings_module, "DEFAULT_TEMPLATE_DIR", template_dir)

    SettingsRepositoryService(config_path=tmp_path / ".dfprinter" / "config.json").load()

    assert schema_path.read_text(encoding="utf-8") == '{"custom": true}'
