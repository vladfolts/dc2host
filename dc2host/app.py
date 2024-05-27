from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

from .helpers import Host, map_container_path, open_in_browser, run

app = Flask(__name__)
host = Host()


@app.route("/run", methods=["POST"])
def run_git():
    data = _check_dict(request.json)
    if cwd := data.get("cwd"):
        cwd = map_container_path(host, Path(cwd))
    check = data.get("check", True)
    completed = run(data["args"], cwd=cwd, check=check)
    return jsonify({"exit_code": completed.returncode})


@app.route("/open_in_browser", methods=["POST"])
def handle_open_in_browser():
    data = _check_dict(request.json)
    file = map_container_path(host, Path(data["file"]))
    open_in_browser(file, data.get("lineNumber"))
    return jsonify(None)


def _check_dict(data):
    if not isinstance(data, dict):
        raise BadRequest(f"Expected a json dictionary, got {type(data)}")
    return data