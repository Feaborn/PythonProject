import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from log_analyzer.cli import process_cli_arguments, validate_files


def test_validate_files(tmp_path):
    """Тест проверки существования файлов"""
    test_file = tmp_path / "test.log"
    test_file.write_text("test")
    assert validate_files([str(test_file)]) == [test_file]


def test_validate_files_not_found():
    """Тест обработки отсутствующих файлов"""
    with pytest.raises(FileNotFoundError):
        validate_files(["nonexistent.log"])


def test_validate_files_multiple(tmp_path):
    """Тест проверки нескольких файлов"""
    file1 = tmp_path / "file1.log"
    file2 = tmp_path / "file2.log"
    file1.write_text("test")
    file2.write_text("test")

    result = validate_files([str(file1), str(file2)])
    assert len(result) == 2
    assert all(isinstance(f, Path) for f in result)


@patch('log_analyzer.cli.validate_files')
@patch('log_analyzer.cli.get_report_class')
@patch('log_analyzer.cli.ProcessPoolExecutor')
def test_process_cli_arguments(mock_pool, mock_get_report, mock_validate):
    """Тест обработки аргументов командной строки"""
    # Настраиваем моки
    mock_validate.return_value = [Path("test.log")]

    # Создаем mock для класса отчета и его экземпляра
    mock_report_class = MagicMock()
    mock_report_instance = MagicMock()
    mock_report_class.return_value = mock_report_instance
    mock_get_report.return_value = mock_report_class

    # Настраиваем ProcessPoolExecutor
    mock_pool_instance = MagicMock()
    mock_pool.return_value.__enter__.return_value = mock_pool_instance
    mock_pool_instance.map.return_value = [{'handlers': {}, 'total': 1}]

    # Мокаем sys.argv
    with patch('sys.argv', ['main.py', 'test.log', '--report', 'handlers']):
        process_cli_arguments()

        # Проверяем вызовы
        mock_validate.assert_called_once_with(['test.log'])
        mock_get_report.assert_called_once_with("handlers")
        mock_report_class.assert_called_once()
        mock_pool_instance.map.assert_called_once()
        mock_report_instance.merge_results.assert_called_once_with([{'handlers': {}, 'total': 1}])
        mock_report_instance.print_report.assert_called_once()


@patch('log_analyzer.cli.validate_files')
def test_process_cli_arguments_invalid_report(mock_validate, capsys):
    """Тест обработки неверного имени отчета"""
    mock_validate.return_value = [Path("test.log")]

    with patch('sys.argv', ['main.py', 'test.log', '--report', 'invalid']), \
            patch('log_analyzer.cli.get_report_class', side_effect=ValueError("Invalid report")):
        with pytest.raises(SystemExit):
            process_cli_arguments()

        captured = capsys.readouterr()
        assert "Invalid report" in captured.out