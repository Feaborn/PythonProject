import argparse
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ProcessPoolExecutor
from functools import partial

from log_analyzer.reports import get_report_class


def validate_files(file_paths: List[str]) -> List[Path]:
    """Проверяет существование файлов."""
    valid_files = []
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        valid_files.append(path)
    return valid_files


def process_single_file(file_path: Path, report_class: Any) -> Dict[str, Any]:
    """Обрабатывает один файл и возвращает данные для отчета."""
    parser = report_class.get_parser()
    data = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if parsed := parser(line):
                data.append(parsed)

    return report_class.process_data(data)


def process_cli_arguments():
    """Обрабатывает аргументы командной строки."""
    parser = argparse.ArgumentParser(description='Analyze Django logs and generate reports.')
    parser.add_argument('log_files', nargs='+', help='Paths to log files')
    parser.add_argument('--report', required=True, help='Report type to generate')
    args = parser.parse_args()

    try:
        # Получаем класс отчета один раз
        report_class = get_report_class(args.report)

        # Проверка файлов
        valid_files = validate_files(args.log_files)

        # Создаем экземпляр отчета для объединения результатов
        report_instance = report_class()

        # Параллельная обработка файлов
        with ProcessPoolExecutor() as executor:
            # Используем partial вместо lambda для Windows-совместимости
            process_func = partial(process_single_file, report_class=report_class)
            results = list(executor.map(process_func, valid_files))

        # Объединение результатов и вывод
        merged = report_instance.merge_results(results)
        report_instance.print_report(merged)

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    process_cli_arguments()