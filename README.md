# Introduction

`dc2host` python package is intended to be used for interaction between VS Code running Dev Containers and other development tools that run on the host system (e.g. `git difftool` etc).
It also contains a command line interface that can be used without VS Code just to open a source file from a local Git repository in GitLab/GitHub Web UI with the specified line number selected.

## `git difftool` example

Suppose you have your favorite GUI `git difftool` configured to run from VS Code for the current file. This setup won't work when you start using Dev Containers because your host system is isolated from VS Code Server and file paths are different for what VS Code sees in a container and for what `git difftool` sees on the host.

To resolve this problem `dc2host` runs a simple REST server on the host that handles requests from Dev Containers and knows how to translate file paths to use them on the host.

# Supported REST endpoints

## git command

```
POST /run_git
{
    "cwd": <container directory where from to execute the specified git command>,
    "args": ["arguments", "for", "git"]
}
```

The git repo directory is guessed from "cwd".

Example:
```shell
curl -d "{\"args\": [\"difftool\", \"file/relative/path\"], \"cwd\": \"/workspace/directory\"}" -H "Content-Type: application/json" host.docker.internal:5000/run_git
```                


## gitk command

```
POST /run_gitk
{
    "cwd": <container directory where from to execute the specified gitk command>,
    "args": ["arguments", "for", "gitk"]
}
```

The git repo directory is guessed from "cwd".

Example:
```shell
curl -d "{\"args\": [\"file/relative/path\"], \"cwd\": \"/workspace/directory\"}" -H "Content-Type: application/json" host.docker.internal:5000/run_gitk
```                

## open_in_browser command

Opens the specified file from a local repo in web browser on GitHub. 

```
POST /open_in_browser
{
    "file": <file path in a container directory>,
    "lineNumber": <line number to highlight (optional)>
}
```

Example:
```shell
curl -d "{\"file\": \"file1.txt\", \"lineNumber\": 42}" -H "Content-Type: application/json" host.docker.internal:5000/run_gitk
```                

# Quick start

Run Flask on Windows host:
```shell
python -m flask --app dc2host.app run --debug --host=0.0.0.0
```

## Configure VS Code "tasks.json"

```json
{
    "tasks": [
        {
            "label": "Open in GitHub",
            "type": "process",
            "command": "curl",
            "args": [
                "-d",
                "{\"file\": \"${file}\", \"lineNumber\": ${lineNumber}}",
                "-H",
                "Content-Type: application/json",
                "host.docker.internal:5000/open_in_browser"
            ],
        },
        {
            "label": "Diff current file",
            "type": "process",
            "command": "curl",
            "args": [
                "-d",
                "{\"args\": [\"difftool\", \"${relativeFile}\"], \"cwd\": \"${workspaceFolder}\"}",
                "-H",
                "Content-Type: application/json",
                "host.docker.internal:5000/run_git"
            ],
        },
        {
            "label": "History current file",
            "type": "process",
            "command": "curl",
            "args": [
                "-d",
                "{\"args\": [\"--\", \"${relativeFile}\"], \"cwd\": \"${workspaceFolder}\"}",
                "-H",
                "Content-Type: application/json",
                "host.docker.internal:5000/run_gitk"
            ],
        }
    ]
}
```

## Configure VS Code "keybindings.json"
```json
[
    {
        "key": "ctrl+k ctrl+d",
        "command": "workbench.action.tasks.runTask",
        "args": "Diff current file"
    }
]
```

## Command line interface
```shell
python -m dc2host open <path to file in repo> 
```
