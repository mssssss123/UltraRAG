"""Flask application exposing a lightweight UltraRAG orchestration API."""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory

from . import pipeline_manager as pm

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
EXAMPLES_DIR = BASE_DIR.parent.parent / "examples"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

    @app.errorhandler(pm.PipelineManagerError)
    def handle_pipeline_error(err: pm.PipelineManagerError):
        LOGGER.error("Pipeline manager error: %s", err)
        return jsonify({"error": str(err)}), 400

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/api/templates", methods=["GET"])
    def list_templates():
        templates: list[dict[str, Any]] = []
        for template_file in sorted(EXAMPLES_DIR.glob("*.yaml")):
            with template_file.open("r", encoding="utf-8") as handle:
                templates.append(
                    {
                        "name": template_file.stem,
                        "content": handle.read(),
                    }
                )
        return jsonify(templates)

    @app.route("/api/servers", methods=["GET"])
    def servers():
        return jsonify(pm.list_servers())

    @app.route("/api/tools", methods=["GET"])
    def tools():
        tool_payload = [
            {
                "id": tool.identifier,
                "server": tool.server,
                "tool": tool.tool,
                "kind": tool.kind,
                "input": tool.input_spec,
                "output": tool.output_spec,
            }
            for tool in pm.list_server_tools()
        ]
        return jsonify(tool_payload)

    @app.route("/api/pipelines", methods=["GET"])
    def pipelines():
        return jsonify(pm.list_pipelines())

    @app.route("/api/pipelines", methods=["POST"])
    def save_pipeline():
        payload: Dict[str, Any] = request.get_json(force=True)  # type: ignore[assignment]
        saved = pm.save_pipeline(payload)
        return jsonify(saved)

    @app.route("/api/pipelines/<string:name>", methods=["GET"])
    def load_pipeline(name: str):
        config = pm.load_pipeline(name)
        return jsonify(config)

    @app.route("/api/pipelines/<string:name>", methods=["DELETE"])
    def remove_pipeline(name: str):
        pm.delete_pipeline(name)
        return jsonify({"status": "deleted"})

    @app.route("/api/pipelines/<string:name>/build", methods=["POST"])
    def build_pipeline(name: str):
        return jsonify(pm.build(name))

    @app.route("/api/pipelines/<string:name>/run", methods=["POST"])
    def run_pipeline(name: str):
        return jsonify(pm.run(name, wait=False))

    @app.route("/api/pipelines/<string:name>/chat", methods=["POST"])
    def chat_pipeline(name: str):
        payload: Dict[str, Any] = request.get_json(force=True)  # type: ignore[assignment]
        question = payload.get("question", "") if isinstance(payload, dict) else ""
        return jsonify(pm.chat(name, question))

    @app.route("/api/logs/run", methods=["GET"])
    def run_logs():
        since = request.args.get("since", default=-1, type=int)
        run_id = request.args.get("run_id") or None
        payload = pm.fetch_run_logs(since=since, run_id=run_id)
        return jsonify(payload)

    @app.route("/api/system/shutdown", methods=["POST"])
    def shutdown():
        LOGGER.info("Shutdown requested via API")
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            LOGGER.warning("Shutdown hook unavailable, falling back to os._exit")
            threading.Timer(0.5, os._exit, args=(0,)).start()
            return jsonify({"status": "shutting-down", "mode": "force"})
        threading.Timer(0.2, func).start()
        return jsonify({"status": "shutting-down", "mode": "graceful"})

    @app.route("/api/pipelines/<string:name>/parameters", methods=["GET"])
    def get_parameters(name: str):
        params = pm.load_parameters(name)
        return jsonify(params)

    @app.route("/api/pipelines/<string:name>/parameters", methods=["PUT"])
    def save_parameters(name: str):
        payload: Dict[str, Any] = request.get_json(force=True)  # type: ignore[assignment]
        pm.save_parameters(name, payload)
        return jsonify({"status": "saved"})

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5050, debug=True)
