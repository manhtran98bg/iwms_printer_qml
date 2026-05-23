class PrinterAppError(Exception):
    """Base application error."""


class PrintRequestError(PrinterAppError):
    """Raised when a print request is invalid."""


class TemplateError(PrinterAppError):
    """Raised when a template cannot be loaded or rendered."""


class SpoolerError(PrinterAppError):
    """Raised when the Windows spooler cannot accept a print job."""
