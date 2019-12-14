import vim
from vim_coveragepy import CoveragePy as _CoveragePy

_obj = _CoveragePy(vim)


def show(*args):
    return _obj.show(args)


def toggle(*args):
    return _obj.toggle(args)


def go_next_problem(*args):
    return _obj.go_next_problem(args)


def show_pytest_context(*args):
    return _obj.show_pytest_context(args)
