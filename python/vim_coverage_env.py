import os
import sys

import vim


def _get_python_binary(exec_prefix):
    try:
        default = vim.eval("g:pymode_python").strip()
    except vim.error:
        default = ""
    if default and os.path.exists(default):
        return default
    if sys.platform[:3] == "win":
        return exec_prefix / "python.exe"
    return exec_prefix / "bin" / "python3"


def _get_pip(venv_path):
    if sys.platform[:3] == "win":
        return venv_path / "Scripts" / "pip.exe"
    return venv_path / "bin" / "pip"


def _get_virtualenv_site_packages(venv_path, pyver):
    if sys.platform[:3] == "win":
        return venv_path / "Lib" / "site-packages"
    return venv_path / "lib" / f"python{pyver[0]}.{pyver[1]}" / "site-packages"


def init(upgrade=False):
    pyver = sys.version_info[:2]
    if pyver < (3, 6):
        print("Sorry, CoveragePy requires Python 3.6+ to run.")
        return False

    from pathlib import Path
    import subprocess
    import venv

    virtualenv_path = Path(vim.eval("g:coveragepy_virtualenv")).expanduser()
    virtualenv_site_packages = str(
        _get_virtualenv_site_packages(virtualenv_path, pyver)
    )
    first_install = False
    if not virtualenv_path.is_dir():
        print("Please wait, one time setup for CoveragePy.")
        _executable = sys.executable
        try:
            sys.executable = str(_get_python_binary(Path(sys.exec_prefix)))
            print(f"Creating a virtualenv in {virtualenv_path}...")
            print(
                "(this path can be customized in .vimrc by setting g:coveragepy_virtualenv)"
            )
            venv.create(virtualenv_path, with_pip=True)
        finally:
            sys.executable = _executable
        first_install = True
    if first_install:
        print("Installing CoveragePy with pip...")
    if upgrade:
        print("Upgrading CoveragePy with pip...")
    if first_install or upgrade:
        subprocess.run(
            [str(_get_pip(virtualenv_path)), "install", "-U", "coverage>=5.0b1"],
            stdout=subprocess.PIPE,
        )
        print("DONE!")
    if first_install:
        print(
            "Pro-tip: to upgrade CoveragePy in the future, use the :CoveragePyUpgrade command and restart Vim.\n"
        )
    if virtualenv_site_packages not in sys.path:
        sys.path.append(virtualenv_site_packages)
    return True
