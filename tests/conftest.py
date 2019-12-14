from unittest import mock

import pytest


@pytest.fixture
def get_coverage(monkeypatch):
    cov_mock = mock.Mock()
    monkeypatch.setattr(
        "vim_coveragepy.VimCoveragePy._get_coverage",
        lambda *a, **kw: (cov_mock.cov, cov_mock.cov_data),
    )
    return cov_mock.cov, cov_mock.cov_data


@pytest.fixture
def cov_data(get_coverage):
    return get_coverage[1]
