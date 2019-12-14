from typing import Any, Sequence

import pynvim

from .util import VimCoveragePy


@pynvim.plugin
class CoveragePy(object):
    def __init__(self, vim: pynvim.Nvim):
        self.plugin = VimCoveragePy(vim)

    @pynvim.function("CoveragePyShow")
    def show(self, args: Sequence[Any]) -> None:
        self.plugin.show(*args)

    @pynvim.function("CoveragePyToggle")
    def toggle(self, args: Sequence[Any]) -> None:
        self.plugin.toggle(*args)

    @pynvim.function("CoveragePyNext")
    def go_next_problem(self, args: Sequence[Any]) -> None:
        self.plugin.go_next_problem(*args)

    @pynvim.function("CoveragePyTestContext")
    def show_pytest_context(self, args: Sequence[Any]) -> None:
        self.plugin.show_pytest_context(*args)
