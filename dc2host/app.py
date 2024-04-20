from pathlib import Path

from flask import Flask, jsonify, request

from .helpers import map_container_path_to_git, open_in_browser, repo_file_url, run

app = Flask(__name__)


@app.route("/run_git", methods=["POST"])
def run_git():
    data = request.json
    git, repo_path = map_container_path_to_git(Path(data["cwd"]))
    cwd = Path(git.working_tree_dir) / repo_path
    run([git.git.git_exec_name] + data["args"], cwd=cwd)
    return jsonify(None)


@app.route("/run_gitk", methods=["POST"])
def run_gitk():
    data = request.json
    git, repo_path = map_container_path_to_git(Path(data["cwd"]))
    cwd = Path(git.working_tree_dir) / repo_path
    run(
        ["gitk"] + data["args"], cwd=cwd, check=False
    )  # gitk return non-zero exit code for normal operation
    return jsonify(None)


@app.route("/open_in_browser", methods=["POST"])
def handle_open_in_browser():
    data = request.json
    git, rel_path = map_container_path_to_git(Path(data["file"]))
    open_in_browser(git, rel_path, data.get("lineNumber"))
    return jsonify(None)
