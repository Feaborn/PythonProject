import re
from collections import defaultdict
from typing import Dict, Any, List, Optional, Callable

from log_analyzer.reports.base import BaseReport


class HandlersReport:
    LOG_PATTERN = re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} '
        r'(?P<level>\w+) '
        r'django.request: '
        r'(?:GET|POST|PUT|DELETE|PATCH|Internal Server Error:) '
        r'(?P<handler>/[^\s\?]+)'  # Останавливаемся на ? или пробеле
    )

    @classmethod
    def get_parser(cls) -> Callable[[str], Optional[Dict[str, str]]]:
        """Возвращает функцию для парсинга строк логов."""
        def parse_line(line: str) -> Optional[Dict[str, str]]:
            if 'django.request:' not in line:
                return None

            match = cls.LOG_PATTERN.match(line.strip())
            if not match:
                return None

            level = match.group('level').upper()
            if level not in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}:
                return None

            return {
                'handler': match.group('handler'),
                'level': level
            }
        return parse_line  # Возвращаем саму функцию, а не её результат!

    @classmethod
    def process_data(cls, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Обрабатывает данные из одного файла."""
        result = defaultdict(lambda: defaultdict(int))
        total = 0

        for entry in data:
            handler = entry['handler']
            level = entry['level']
            result[handler][level] += 1
            total += 1

        return {
            'handlers': dict(result),
            'total': total
        }

    @classmethod
    def merge_results(cls, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Объединяет результаты обработки нескольких файлов."""
        merged_handlers = defaultdict(lambda: defaultdict(int))
        total = 0

        for result in results:
            for handler, levels in result['handlers'].items():
                for level, count in levels.items():
                    merged_handlers[handler][level] += count
            total += result['total']

        return {
            'handlers': dict(merged_handlers),
            'total': total
        }

    @classmethod
    def print_report(cls, report_data: Dict[str, Any]):
        """Выводит отчет в консоль."""
        handlers_data = report_data['handlers']
        total = report_data['total']

        # Определяем все уровни логирования
        all_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        # Заголовок
        print(f"Total requests: {total}\n")
        header = "HANDLER".ljust(25)
        for level in all_levels:
            header += f"\t{level}"
        print(header)

        # Данные по обработчикам
        totals_by_level = defaultdict(int)
        for handler in sorted(handlers_data.keys()):
            line = handler.ljust(25)
            for level in all_levels:
                count = handlers_data[handler].get(level, 0)
                line += f"\t{count}"
                totals_by_level[level] += count
            print(line)

        # Итоги по уровням
        footer = "".ljust(25)
        for level in all_levels:
            footer += f"\t{totals_by_level[level]}"
        print(footer)