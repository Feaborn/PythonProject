from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseReport(ABC):
    """Базовый класс для всех отчетов."""

    @classmethod
    @abstractmethod
    def get_parser(cls):
        """Возвращает функцию для парсинга строки лога."""
        pass

    @classmethod
    @abstractmethod
    def process_data(cls, data: list) -> Dict[str, Any]:
        """Обрабатывает данные из одного файла."""
        pass

    @classmethod
    @abstractmethod
    def merge_results(cls, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Объединяет результаты обработки нескольких файлов."""
        pass

    @classmethod
    @abstractmethod
    def print_report(cls, report_data: Dict[str, Any]):
        """Выводит отчет в консоль."""
        pass