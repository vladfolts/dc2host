from pathlib import Path
import subprocess
from shlex import quote
from typing import Generator
from urllib.parse import SplitResult, urlsplit, urlunsplit
import webbrowser

import docker
from docker.models.containers import Container
from git import Repo


def _gen_bind_mounts(container: Container) -> Generator[tuple[str, str], None, None]:
    if mounts := container.attrs["HostConfig"].get("Mounts"):
        for mount in mounts:
            if mount["Type"] == "bind":
                src, dst = mount["Source"], mount["Target"]
                yield src, dst


def docker_bind_mounts() -> Generator[tuple[str, str], None, None]:
    client = docker.from_env()
    for c in client.containers.list():
        yield from _gen_bind_mounts(c)


def git_remote(repo_path: str):
    repo = Repo(repo_path)
    return repo.remotes.origin.url


def run(args, check=True, cwd=None, **kwargs) -> subprocess.CompletedProcess:
    msg = "run: " + " ".join(map(quote, args))
    if cwd:
        msg += f" (in '{cwd}')"
    print(msg, flush=True)
    return subprocess.run(args, check=check, cwd=cwd, **kwargs)


def repo_root_url(remote_url) -> SplitResult:
    result = remote_url.removesuffix(".git")
    git_prefix = "git@"
    if result.startswith(git_prefix):
        result = result[len(git_prefix) :]
        host, host_path = result.split(":", 1)
        result = "https://" + host + "/" + host_path
    return urlsplit(result)


def repo_file_url(
    remote_url: str, path: Path, line: int | None = None, branch: str = "master"
):
    url_parts = repo_root_url(remote_url)
    branch_path = {"github.com": f"/blob/{branch}/{path}"}.get(url_parts.hostname, f"/-/blob/{branch}/{path}")
    url_parts = url_parts._replace(path=url_parts.path + branch_path)
    if line is not None:
        url_parts = url_parts._replace(fragment=f"L{line}")
    return urlunsplit(url_parts)


def map_container_path_to_git(path: Path) -> tuple[Repo, Path]:
    for src, dst in docker_bind_mounts():
        try:
            rel_path = path.relative_to(dst)
        except ValueError:
            pass
        else:
            return Repo(src), rel_path

    raise ValueError(f"Path {path} is not in any bind mounts")


def open_in_browser(git: Repo, rel_path: Path, line: int | None):
    url = repo_file_url(
        git.remotes.origin.url,
        rel_path,
        line=line,
        branch=git.active_branch,
    )
    webbrowser.open(url)
