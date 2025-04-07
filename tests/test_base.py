import pytest
from abc import ABC, abstractmethod
from log_analyzer.reports.base import BaseReport


def test_base_report_abstract_methods():
    """Тест, что абстрактные методы BaseReport действительно требуют реализации"""
    with pytest.raises(TypeError):
        # Попытка создать класс без реализации абстрактных методов
        class InvalidReport(BaseReport):
            pass

        # Создаем экземпляр, чтобы проверить ошибку
        InvalidReport()


def test_base_report_implementation():
    """Тест корректной реализации отчета"""
    class ValidReport(BaseReport):
        @classmethod
        def get_parser(cls):
            return lambda x: x

        @classmethod
        def process_data(cls, data):
            return {}

        def merge_results(self, results):
            return {}

        def print_report(self, merged_data):
            pass

    # Должно создаваться без ошибок
    report = ValidReport()
    assert isinstance(report, BaseReport)