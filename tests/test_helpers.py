from urllib.parse import SplitResult
from d2host.helpers import repo_root_url


def test_repo_root_url_with_git_prefix():
    assert repo_root_url("git@example.com:namespace/repo.git") == SplitResult(
        scheme="https",
        netloc="example.com",
        path="/namespace/repo",
        query="",
        fragment="",
    )


def test_repo_root_url_with_https_prefix():
    assert repo_root_url("https://github.com/namespace/repo.git") == SplitResult(
        scheme="https",
        netloc="github.com",
        path="/namespace/repo",
        query="",
        fragment="",
    )
