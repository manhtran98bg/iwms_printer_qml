from __future__ import annotations

import json

from src.services.print_template_service import PrintTemplateService


def test_render_resolves_nested_fields_and_margin_tokens():
    service = PrintTemplateService()
    template = "\n".join(
        (
            "^LS{{margin_left}}",
            "^LT{{margin_top}}",
            "^FO0,0^FDmaster_data.packing_kit_0^FS",
        )
    )

    rendered = service.render(
        template,
        [{"master_data": {"packing_kit": "KIT604"}}],
        columns=1,
        margin_left=-7,
        margin_top=14,
    )[0]

    assert "^LS-7" in rendered
    assert "^LT14" in rendered
    assert "^FO0,0^FDKIT604^FS" in rendered


def test_save_print_settings_preserves_schema_content(tmp_path):
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "require": ["parts_no"],
                "templateFile": "template.zpl",
                "printSettings": {"margin_left": 0, "margin_top": 0},
                "defaults": {"parts_no": "RU1-0404"},
            }
        ),
        encoding="utf-8",
    )

    service = PrintTemplateService()
    service.save_print_settings(str(schema_path), margin_left=10, margin_top=-10)

    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    assert payload["printSettings"] == {"margin_left": 10, "margin_top": -10}
    assert payload["require"] == ["parts_no"]
    assert payload["defaults"] == {"parts_no": "RU1-0404"}
