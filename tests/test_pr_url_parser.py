import pytest

from app.github.pr_url_parser import parse_pr_url


def test_parse_valid_github_pr_url():
    ref = parse_pr_url("https://github.com/Tristan8545/AI-PR-Review/pull/12")

    assert ref.owner == "Tristan8545"
    assert ref.repo == "AI-PR-Review"
    assert ref.number == 12


def test_reject_invalid_url():
    with pytest.raises(ValueError):
        parse_pr_url("https://github.com/Tristan8545/AI-PR-Review")

