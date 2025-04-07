import pytest
from pathlib import Path
from log_analyzer.parser import parse_log_file


def test_parse_log_file_valid_entries(tmp_path):
    """Тест корректных записей django.request"""
    test_file = tmp_path / "valid.log"
    test_file.write_text(
        "2023-01-01 12:00:00,123 INFO django.request: GET /api/v1/test/\n"
        "2023-01-01 12:00:01,456 ERROR django.request: POST /api/v1/error/\n"
    )

    results = parse_log_file(test_file)
    assert len(results) == 2
    assert results[0] == {"level": "INFO", "handler": "/api/v1/test/"}
    assert results[1]["level"] == "ERROR"


def test_parse_log_file_invalid_levels(tmp_path):
    """Тест некорректных уровней логирования"""
    test_file = tmp_path / "invalid_levels.log"
    test_file.write_text(
        "2023-01-01 12:00:00,123 UNKNOWN django.request: GET /api/v1/test/\n"
        "2023-01-01 12:00:01,456 INFO django.request: GET /api/v1/valid/\n"
    )

    results = parse_log_file(test_file)
    assert len(results) == 1  # Должен остаться только валидный уровень INFO
    assert results[0]["level"] == "INFO"


def test_parse_log_file_empty(tmp_path):
    """Тест пустого файла"""
    test_file = tmp_path / "empty.log"
    test_file.write_text("")
    assert parse_log_file(test_file) == []


def test_parse_log_file_nonexistent():
    """Тест несуществующего файла"""
    with pytest.raises(FileNotFoundError):
        parse_log_file(Path("nonexistent.log"))


def test_parse_log_file_invalid_levels(tmp_path):
    """Тест некорректных уровней логирования"""
    test_file = tmp_path / "invalid_levels.log"
    test_file.write_text(
        "2023-01-01 12:00:00,123 UNKNOWN django.request: GET /api/v1/test/\n"
    )
    assert parse_log_file(test_file) == []