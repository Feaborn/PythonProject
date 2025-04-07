import pytest
from log_analyzer.reports.handlers import HandlersReport
from collections import defaultdict


def test_get_parser_returns_callable():
    parser = HandlersReport.get_parser()
    assert callable(parser)


def test_parser_with_valid_request():
    line = "2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/test/ 200 OK [192.168.1.1]"
    result = HandlersReport.get_parser()(line)
    assert result == {'handler': '/api/v1/test/', 'level': 'INFO'}


def test_parser_with_error_request():
    line = "2025-03-28 12:11:57,000 ERROR django.request: Internal Server Error: /api/v1/test/ [192.168.1.1] - Error"
    result = HandlersReport.get_parser()(line)
    assert result == {'handler': '/api/v1/test/', 'level': 'ERROR'}


def test_parser_ignores_non_request_logs():
    line = "2025-03-28 12:25:45,000 DEBUG django.db.backends: SELECT * FROM table"
    assert HandlersReport.get_parser()(line) is None


def test_process_data_empty_input():
    result = HandlersReport.process_data([])
    assert result == {'handlers': {}, 'total': 0}


def test_process_data_single_entry():
    data = [{'handler': '/test', 'level': 'INFO'}]
    result = HandlersReport.process_data(data)
    assert result == {
        'handlers': {'/test': {'INFO': 1}},
        'total': 1
    }


def test_process_data_multiple_entries():
    data = [
        {'handler': '/test', 'level': 'INFO'},
        {'handler': '/test', 'level': 'ERROR'},
        {'handler': '/api', 'level': 'INFO'}
    ]
    result = HandlersReport.process_data(data)
    assert result['total'] == 3
    assert result['handlers']['/test'] == {'INFO': 1, 'ERROR': 1}
    assert result['handlers']['/api'] == {'INFO': 1}


def test_merge_results_empty():
    assert HandlersReport.merge_results([]) == {'handlers': {}, 'total': 0}


def test_merge_results_multiple_files():
    results = [
        {'handlers': {'/test': {'INFO': 1}}, 'total': 1},
        {'handlers': {'/test': {'ERROR': 1}, '/api': {'INFO': 2}}, 'total': 3}
    ]
    merged = HandlersReport.merge_results(results)
    assert merged['total'] == 4
    assert merged['handlers']['/test'] == {'INFO': 1, 'ERROR': 1}
    assert merged['handlers']['/api'] == {'INFO': 2}


def test_print_report_formatting(capsys):
    test_data = {
        'handlers': {
            '/api': {'INFO': 2, 'ERROR': 1},
            '/test': {'INFO': 1}
        },
        'total': 3
    }
    HandlersReport.print_report(test_data)
    captured = capsys.readouterr()

    # Проверяем базовую структуру вывода
    assert "Total requests: 3" in captured.out
    assert "HANDLER" in captured.out
    assert "/api" in captured.out
    assert "/test" in captured.out
    assert "INFO" in captured.out
    assert "ERROR" in captured.out


def test_edge_case_url_formats():
    test_cases = [
        ("GET /api/v1/test/?param=value", '/api/v1/test/'),
        ("POST /api/v1/users/123", '/api/v1/users/123'),
        ("Internal Server Error: /api/v1/error/", '/api/v1/error/')
    ]

    for input_url, expected in test_cases:
        line = f"2025-01-01 12:00:00,000 INFO django.request: {input_url}"
        result = HandlersReport.get_parser()(line)
        assert result['handler'] == expected