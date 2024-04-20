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
            "label": "Open in Gitlab",
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
