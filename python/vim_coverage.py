import os
import re
import sys
from typing import Any, Dict, List, Set, Tuple, Union

import coverage


class Editor:
    SIGN_WARNING = "coverageWarn"
    SIGN_ERROR = "coverageErr"
    SIGN_OK = "coverageOk"

    def __init__(self) -> None:
        self._module = None
        self._sign_offset = 5000000
        self._lines_with_problems: Dict[str, Set[int]] = {}

    @property
    def _vim(self) -> Any:
        if not self._module:
            import vim

            self._module = vim
        return self._module

    def _store_signs(self, filename: str, signs: List[Dict[str, Any]]) -> None:
        problems = []
        in_covered_range = True
        for sign in sorted(signs, key=lambda s: s["line"]):
            if sign["name"] == Editor.SIGN_ERROR or sign["name"] == Editor.SIGN_WARNING:
                if in_covered_range:
                    problems.append(sign["line"])
                    in_covered_range = False
            else:
                in_covered_range = True
        self._lines_with_problems[filename] = problems  # type: ignore

    def _place_sign(self, id: int, line: int, name: str, file: str) -> None:
        self._vim.command(
            "sign place {id} line={line} name={name} group=CoveragePyGroup file={file}".format(
                id=id, line=line, name=name, file=file
            )
        )

    @property
    def sign_offset(self) -> int:
        return self._sign_offset

    @sign_offset.setter
    def sign_offset(self, val: Union[str, int]) -> None:
        self._sign_offset = int(val)

    def message(self, message: str) -> None:
        print(message)

    def show_coverage(self, filename: str, signs: List[Dict[str, Any]]) -> None:
        if not signs:
            return
        if self.is_sign_shown(filename):
            self.clear_signs(filename)
        self._store_signs(filename, signs)
        for sign in signs:
            self._place_sign(
                id=sign["line"] + self.sign_offset,
                line=sign["line"],
                name=sign["name"],
                file=filename,
            )

    def _unplace_signs(self, filename: str) -> None:
        self._vim.command(
            "sign unplace * group=CoveragePyGroup file={file}".format(file=filename)
        )

    def clear_signs(self, filename: str) -> None:
        if not self.is_sign_shown(filename):
            return
        self._unplace_signs(filename)
        del self._lines_with_problems[filename]

    def is_sign_shown(self, filename: str) -> bool:
        return filename in self._lines_with_problems

    def show_list_of_tests(self, whats: List[Dict[str, Any]]) -> None:
        cmd = f':call setqflist({whats}, "r")'
        self._vim.command(cmd)
        self._vim.command(":copen")

    def move_to_next_problem(self, filename: str, current_line: int) -> None:
        for i, line in enumerate(self._lines_with_problems[filename]):
            if line > current_line:
                self._vim.current.window.cursor = (line, 0)
                return


class OldVim(Editor):
    def __init__(self) -> None:
        super().__init__()
        self._sign_ids: Dict[str, Set[int]] = {}

    def _store_signs(self, filename: str, signs: List[Dict[str, Any]]) -> None:
        super()._store_signs(filename, signs)
        self._sign_ids[filename] = {s["line"] for s in signs}

    def _place_sign(self, id: int, line: int, name: str, file: str) -> None:
        self._vim.command(
            "sign place {id} line={line} name={name} file={file}".format(
                id=id, line=line, name=name, file=file
            )
        )

    def _unplace_signs(self, filename: str) -> None:
        for sign in self._sign_ids[filename]:
            self._vim.command(
                "sign unplace {id} file={file}".format(
                    id=sign + self.sign_offset, file=filename
                )
            )

    def clear_signs(self, filename: str) -> None:
        super().clear_signs(filename)
        del self._sign_ids[filename]


editor = Editor()


def downgrade_editor() -> None:
    global editor
    editor = OldVim()


def _get_coverage(cov_file: str) -> Tuple[coverage.Coverage, coverage.CoverageData]:
    cov = coverage.Coverage(cov_file)
    cov_data = cov.get_data()
    cov_data.read()
    return cov, cov_data


def _get_file_coverage(
    cov_file: str, filename: str
) -> Tuple[Set[int], Set[int], Set[int]]:
    cov, _ = _get_coverage(cov_file)
    analysis = cov._analyze(filename)

    missing_branch_arcs = analysis.missing_branch_arcs()
    return analysis.statements, analysis.missing, missing_branch_arcs.keys()


def coverage_show(cov_file: str, filename: str) -> None:
    statements, missing, missing_branches = _get_file_coverage(cov_file, filename)
    signs = []
    for lineno in statements:
        if lineno in missing:
            name = editor.SIGN_ERROR
        elif lineno in missing_branches:
            name = editor.SIGN_WARNING
        else:
            name = editor.SIGN_OK
        signs.append({"line": lineno, "name": name})
    editor.show_coverage(filename, signs)


def coverage_toggle(cov_file: str, filename: str) -> None:
    if editor.is_sign_shown(filename):
        editor.clear_signs(filename)
    else:
        coverage_show(cov_file, filename)


PYTEST_CONTEXT = r"(?P<path>[^:]+)::(?P<testclass>\w+::)?(?P<test>\w+)(?P<params>\[[^\]]+\])?\|?(?P<step>\w+)?"


def coverage_line(cov_file: str, filename: str, line: str) -> None:
    _, cov_data = _get_coverage(cov_file)
    context = cov_data.contexts_by_lineno(filename)
    lineno = int(line)
    if lineno not in context:
        editor.message("Line was not executed.")
        return
    tests = []
    for row in context[lineno]:
        m = re.match(PYTEST_CONTEXT, row)
        if m:
            groups = m.groupdict()
            if groups["step"] == "run":
                tests.append(
                    {
                        "filename": os.path.join(
                            os.path.dirname(cov_file), groups["path"]
                        ),
                        "pattern": ("  def " if groups["testclass"] else "def ")
                        + groups["test"],
                    }
                )
    if tests:
        editor.show_list_of_tests(tests)


def coverage_next_problem(cov_file: str, filename: str, line: str) -> None:
    if not editor.is_sign_shown(filename):
        coverage_show(cov_file, filename)
    editor.move_to_next_problem(filename, int(line))


def coverage_version() -> None:
    editor.message(
        "CoveragePy, version %s on Python %s." % (coverage.__version__, sys.version)
    )
