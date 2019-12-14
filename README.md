# Vim 8.0+ / NeoVim Python Coverage plugin

The aim of the project is:

- Display coverage information in SignColumn
- Show tests where current line was executed (pytest and coverage 5+ only)
- Go to next uncovered chunk of code

## Install

For vim-plug

    if has('nvim')
        Plug 'kalekseev/vim-coverage.py', { 'do': ':UpdateRemotePlugins' }
    else
        Plug 'kalekseev/vim-coverage.py'
        Plug 'roxma/nvim-yarp'
        Plug 'roxma/vim-hug-neovim-rpc'
    endif

## Usage

Editor must be started inside python virtualenv where `coverage` package installed otherwise plugin will try to load global `coverage` module or fail.

- **CoveragePy** - show coverage signs for current buffer
- **CoveragePyToggle** - show / hide coverage
- **CoveragePytestContext** - show tests where current line was executed. Requires py.test and `--cov-context=test` option.
- **CoveragePyNext** - go to next not covered chunk

## Development

Install deps and git hook:

    python3 -m venv env && source env/bin/activate
    pip install -r dev-requirements.txt
    pre-commit install

Lint with:

    pre-commit run -a

Run tests with:

    PYTHONPATH=./rplugin/python3/ py.test --cov=rplugin --cov-branch --cov-context=test
