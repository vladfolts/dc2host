import subprocess
import webbrowser
from pathlib import Path
from shlex import quote
from typing import Generator
from urllib.parse import SplitResult, urlsplit, urlunsplit

import docker
from docker.models.containers import Container
from git import Repo
from werkzeug.exceptions import HTTPException


def _gen_bind_mounts(container: Container) -> Generator[tuple[str, str], None, None]:
    if mounts := container.attrs["HostConfig"].get("Mounts"):
        for mount in mounts:
            if mount["Type"] == "bind":
                src, dst = mount["Source"], mount["Target"]
                yield src, dst


class Host:
    def __init__(self):
        self.__docker = docker.from_env()

    def docker_bind_mounts(self) -> Generator[tuple[str, str], None, None]:
        for c in self.__docker.containers.list():
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
    known_hosts_mapping = {"github.com": "/blob/{0}/{1}"}
    default_mapping = "/-/blob/{0}/{1}"

    url_parts = repo_root_url(remote_url)
    if not (host := url_parts.hostname):
        raise HTTPException("Cannot parse remote URL's host: " + remote_url)
    
    fmt = known_hosts_mapping.get(host, default_mapping)
    branch_path = fmt.format(branch, path)
    url_parts = url_parts._replace(path=url_parts.path + branch_path)
    if line is not None:
        url_parts = url_parts._replace(fragment=f"L{line}")
    return urlunsplit(url_parts)


def map_container_path(host: Host, path: Path) -> Path:
    for src, dst in host.docker_bind_mounts():
        try:
            rel_path = path.relative_to(dst)
        except ValueError:
            pass
        else:
            return (src / rel_path).resolve()

    raise ValueError(f"Path {path} is not in any bind mounts")


def open_in_browser(path: Path, line: int | None):
    git = Repo(path if path.is_dir() else path.parent, search_parent_directories=True)
    url = repo_file_url(
        git.remotes.origin.url,
        path.relative_to(git.working_dir),
        line=line,
        branch=git.active_branch,
    )
    webbrowser.open(url)
