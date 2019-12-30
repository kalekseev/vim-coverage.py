import glob
import os
import re
import sys
from typing import TYPE_CHECKING, Any, Dict, List, Set, Tuple, Union

from pynvim import Nvim

if TYPE_CHECKING:
    import coverage


PYTEST_CONTEXT = r"(?P<path>[^:]+)::(?P<testclass>\w+::)?(?P<test>\w+)(?P<params>\[[^\]]+\])?\|?(?P<step>\w+)?"


class Abort(Exception):
    pass


class Editor:
    SIGN_WARNING = "coverageWarn"
    SIGN_ERROR = "coverageErr"
    SIGN_OK = "coverageOk"

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._sign_offset = int(vim.eval("get(g:, 'coveragepy_sign_offset', 5000000)"))
        self._lines_with_problems: Dict[str, Set[int]] = {}

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
        self._vim.out_write(message + "\n")

    def err_message(self, message: str) -> None:
        self._vim.err_write(message + "\n")

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
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
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


class VimCoveragePy:
    def __init__(self, vim: Nvim):
        if vim.eval("has('nvim-0.4.2') || (v:version >= 801 && has('patch614'))"):
            self.editor = Editor(vim)
        else:
            self.editor = OldVim(vim)
        self._coverage = None

    @property
    def coverage_module(self) -> "coverage":
        if not self._coverage:  # pragma: no cover
            if os.environ.get("VIRTUAL_ENV"):
                path = glob.glob(
                    os.environ["VIRTUAL_ENV"] + "/lib/python*/site-packages"
                )
                if path:
                    sys.path.insert(0, path[0])
                try:
                    import coverage
                except ImportError:
                    self.editor.err_message(
                        "Can't import coverage module from $VIRTUAL_ENV."
                    )
                    raise Abort()
                finally:
                    if path:
                        del sys.path[:1]
            else:
                try:
                    import coverage
                except ImportError:
                    self.editor.err_message(
                        "Can't import coverage from g:python3_host_prog site-packages. You may also want to run vim with $VIRTUAL_ENV set."
                    )
                    raise Abort()
            self._coverage = coverage
        return self._coverage

    def _get_coverage(
        self, cov_file: str
    ) -> Tuple["coverage.Coverage", "coverage.CoverageData"]:
        cov = self.coverage_module.Coverage(cov_file)
        cov_data = cov.get_data()
        cov_data.read()
        return cov, cov_data

    def _get_file_coverage(
        self, cov_file: str, filename: str
    ) -> Tuple[Set[int], Set[int], Set[int]]:
        cov, _ = self._get_coverage(cov_file)
        analysis = cov._analyze(filename)

        missing_branch_arcs = analysis.missing_branch_arcs()
        return analysis.statements, analysis.missing, missing_branch_arcs.keys()

    def show(self, cov_file: str, filename: str) -> None:
        statements, missing, missing_branches = self._get_file_coverage(
            cov_file, filename
        )
        signs = []
        for lineno in statements:
            if lineno in missing:
                name = self.editor.SIGN_ERROR
            elif lineno in missing_branches:
                name = self.editor.SIGN_WARNING
            else:
                name = self.editor.SIGN_OK
            signs.append({"line": lineno, "name": name})
        self.editor.show_coverage(filename, signs)

    def toggle(self, cov_file: str, filename: str) -> None:
        if self.editor.is_sign_shown(filename):
            self.editor.clear_signs(filename)
        else:
            self.show(cov_file, filename)

    def go_next_problem(self, cov_file: str, filename: str, line: str) -> None:
        if not self.editor.is_sign_shown(filename):
            self.show(cov_file, filename)
        self.editor.move_to_next_problem(filename, int(line))

    def show_pytest_context(self, cov_file: str, filename: str, line: str) -> None:
        _, cov_data = self._get_coverage(cov_file)
        context = cov_data.contexts_by_lineno(filename)
        lineno = int(line)
        if lineno not in context:
            self.editor.message("Line was not executed.")
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
            self.editor.show_list_of_tests(tests)
