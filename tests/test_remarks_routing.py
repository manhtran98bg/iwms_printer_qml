from __future__ import annotations

from pathlib import Path

import pytest

from src.core.errors import PrintRequestError, TemplateError
from src.models.print_request import PrintRequest
from src.services.print_template_service import PrintTemplateService
from src.services.print_workflow_service import PrintWorkflowService
from src.services.printer_service import PrinterService
from src.services.settings_repository_service import SettingsRepositoryService


def test_template_routing_uses_remarks_values():
    template_service = PrintTemplateService()
    template_root = Path("src/assets/template")
    routed_formats = [
        template_service.load_format(str(template_root / "canon" / "canon_schema.json")),
        template_service.load_format(str(template_root / "assy" / "assy_schema.json")),
    ]

    canon_format = template_service.matching_format({"remarks": "Mau_02"}, routed_formats)
    assy_format = template_service.matching_format({"remarks": "Mau_01"}, routed_formats)

    assert canon_format is not None
    assert canon_format.template_path.endswith("canon_zpl_place_holder.zpl")
    assert assy_format is not None
    assert assy_format.template_path.endswith("assy_zpl_place_holder.zpl")


def test_api_request_validation_rejects_missing_remarks():
    workflow = PrintWorkflowService(
        settings_repository=SettingsRepositoryService(),
        print_template_service=PrintTemplateService(),
        printer_service=PrinterService(),
    )

    with pytest.raises(PrintRequestError, match="remarks"):
        workflow.validate_api_request(PrintRequest(labels=[{"customer": "CANON QV"}]))


def test_api_request_validation_rejects_unknown_remarks():
    workflow = PrintWorkflowService(
        settings_repository=SettingsRepositoryService(),
        print_template_service=PrintTemplateService(),
        printer_service=PrinterService(),
    )

    with pytest.raises(PrintRequestError, match="remarks"):
        workflow.validate_api_request(PrintRequest(labels=[{"remarks": "Mau_99"}]))


def test_api_request_validation_rejects_template_render_errors():
    workflow = PrintWorkflowService(
        settings_repository=SettingsRepositoryService(),
        print_template_service=PrintTemplateService(),
        printer_service=PrinterService(),
    )

    request = PrintRequest(
        labels=[
            {
                "remarks": "Mau_02",
                "production_date": "07-01-2026",
                "label": "49",
            }
        ]
    )

    with pytest.raises(TemplateError, match="production_date_convert"):
        workflow.validate_api_request(request)
