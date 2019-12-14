import unittest
from unittest import mock

from vim_coveragepy.util import VimCoveragePy


class FakePlugin(VimCoveragePy):
    def __init__(self):
        self.editor = mock.Mock()


def test_coverage_show(monkeypatch):
    plugin = FakePlugin()
    plugin._get_file_coverage = mock.Mock(return_value=({1, 2, 3}, {2}, {3}))
    plugin.show(cov_file="/.coverage", filename="a.py")
    plugin._get_file_coverage.assert_called_once_with("/.coverage", "a.py")
    editor = plugin.editor
    editor.show_coverage.assert_called_once_with(
        "a.py",
        [
            {"line": 1, "name": editor.SIGN_OK},
            {"line": 2, "name": editor.SIGN_ERROR},
            {"line": 3, "name": editor.SIGN_WARNING},
        ],
    )


def test_line_not_in_context(cov_data):
    cov_data.contexts_by_lineno.return_value = {}
    plugin = FakePlugin()
    plugin.show_pytest_context(cov_file="/.coverage", filename="a.py", line=3)
    plugin.editor.message.assert_called_once_with("Line was not executed.")


def test_line_parse_pytest_simple(cov_data):
    cov_data.contexts_by_lineno.return_value = {
        3: ["path/to/file.py::test_parse|run", "path/to/file.py::test_parse_next|run"]
    }
    plugin = FakePlugin()
    plugin.show_pytest_context(cov_file="/.coverage", filename="a.py", line=3)
    plugin.editor.show_list_of_tests.assert_called_once_with(
        [
            {"filename": "/path/to/file.py", "pattern": "def test_parse"},
            {"filename": "/path/to/file.py", "pattern": "def test_parse_next"},
        ]
    )


def test_line_parse_pytest_fixture(cov_data):
    cov_data.contexts_by_lineno.return_value = {
        3: ["path/to/file.py::test_parse[True, False]|run"]
    }
    plugin = FakePlugin()
    plugin.show_pytest_context(cov_file="/.coverage", filename="a.py", line=3)
    plugin.editor.show_list_of_tests.assert_called_once_with(
        [{"filename": "/path/to/file.py", "pattern": "def test_parse"}]
    )


def test_line_parse_pytest_unittest(cov_data):
    cov_data.contexts_by_lineno.return_value = {
        3: ["path/to/file.py::TestClass::test_parse|run"]
    }
    plugin = FakePlugin()
    plugin.show_pytest_context(cov_file="/.coverage", filename="a.py", line=3)
    plugin.editor.show_list_of_tests.assert_called_once_with(
        [{"filename": "/path/to/file.py", "pattern": "  def test_parse"}]
    )


def test_get_coverage(monkeypatch):
    plugin = FakePlugin()
    plugin._coverage = mock.Mock()
    plugin._get_coverage("/path/to/.coverage")
    plugin._coverage.Coverage.assert_called_once_with("/path/to/.coverage")


class TestUnittestStyle(unittest.TestCase):
    # repeat for testing purposes
    def test_get_coverage(self):
        plugin = FakePlugin()
        plugin._coverage = mock.Mock()
        plugin._get_coverage("/path/to/.coverage")
        plugin._coverage.Coverage().get_data().read.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
