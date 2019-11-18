# Vim/NeoVim Coverage.py 5.0+ plugin

Requires Vim 7.0+ / NeoVim compiled with python3.6+

## Development

Install deps and git hook:

    pip install -r dev-requirements.txt
    pre-commit install

Lint with:

    pre-commit run -a

Run tests with:

    PYTHONPATH=./python/ py.test --cov=python --cov-branch --cov-context=test
