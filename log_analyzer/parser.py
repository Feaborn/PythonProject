import re
from pathlib import Path
from typing import List, Dict, Any

VALID_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}

def parse_log_file(file_path: Path) -> List[Dict[str, Any]]:
    """Парсит файл логов Django и возвращает список записей."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    entries = []
    pattern = re.compile(
        r'^.*? '
        r'(?P<level>\w+) '
        r'django.request: '
        r'(?P<method>\w+) '
        r'(?P<handler>/[^\s\?]+)'
    )

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if match := pattern.search(line.strip()):
                level = match.group('level').upper()
                if level in VALID_LEVELS:  # Фильтрация по допустимым уровням
                    entries.append({
                        'level': level,
                        'handler': match.group('handler')
                    })

    return entries