import unittest
from unittest import mock

import vim_coverage


def test_coverage_show(editor, monkeypatch):
    get_file_coverage = mock.Mock(return_value=({1, 2, 3}, {2}, {3}))
    monkeypatch.setattr("vim_coverage._get_file_coverage", get_file_coverage)
    vim_coverage.coverage_show(cov_file="/.coverage", filename="a.py")
    get_file_coverage.assert_called_once_with("/.coverage", "a.py")
    editor.show_coverage.assert_called_once_with(
        "a.py",
        [
            {"line": 1, "name": editor.SIGN_OK},
            {"line": 2, "name": editor.SIGN_ERROR},
            {"line": 3, "name": editor.SIGN_WARNING},
        ],
    )


def test_line_not_in_context(editor, cov_data):
    cov_data.contexts_by_lineno.return_value = {}
    vim_coverage.coverage_line(cov_file="/.coverage", filename="a.py", line=3)
    editor.message.assert_called_once_with("Line was not executed.")


def test_line_parse_pytest_simple(editor, cov_data):
    cov_data.contexts_by_lineno.return_value = {
        3: ["path/to/file.py::test_parse|run", "path/to/file.py::test_parse_next|run"]
    }
    vim_coverage.coverage_line(cov_file="/.coverage", filename="a.py", line=3)
    editor.show_list_of_tests.assert_called_once_with(
        [
            {"filename": "/path/to/file.py", "pattern": "def test_parse"},
            {"filename": "/path/to/file.py", "pattern": "def test_parse_next"},
        ]
    )


def test_line_parse_pytest_fixture(editor, cov_data):
    cov_data.contexts_by_lineno.return_value = {
        3: ["path/to/file.py::test_parse[True, False]|run"]
    }
    vim_coverage.coverage_line(cov_file="/.coverage", filename="a.py", line=3)
    editor.show_list_of_tests.assert_called_once_with(
        [{"filename": "/path/to/file.py", "pattern": "def test_parse"}]
    )


def test_line_parse_pytest_unittest(editor, cov_data):
    cov_data.contexts_by_lineno.return_value = {
        3: ["path/to/file.py::TestClass::test_parse|run"]
    }
    vim_coverage.coverage_line(cov_file="/.coverage", filename="a.py", line=3)
    editor.show_list_of_tests.assert_called_once_with(
        [{"filename": "/path/to/file.py", "pattern": "  def test_parse"}]
    )


def test_get_coverage(monkeypatch):
    CoverageMock = mock.Mock()
    monkeypatch.setattr("vim_coverage.coverage.Coverage", CoverageMock)
    vim_coverage._get_coverage("/path/to/.coverage")
    CoverageMock.assert_called_once_with("/path/to/.coverage")


class TestUnittestStyle(unittest.TestCase):
    # repeat for testing purposes
    def test_get_coverage(self):
        with mock.patch("vim_coverage.coverage.Coverage") as CoverageMock:
            vim_coverage._get_coverage("/path/to/.coverage")
            CoverageMock.assert_called_once_with("/path/to/.coverage")
            CoverageMock().get_data().read.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
