from typing import Type
from log_analyzer.reports.handlers import HandlersReport


REPORTS = {
    'handlers': HandlersReport,
}


def get_report_class(report_name: str) -> Type:
    """Возвращает класс отчета по его имени."""
    if report_name not in REPORTS:
        raise ValueError(f"Unknown report type: {report_name}. Available reports: {list(REPORTS.keys())}")
    return REPORTS[report_name]