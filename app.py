from flask import Flask, request, jsonify
import os
import json
from validator import run_validation
from github_uploader import upload_folder_to_github

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")  # username/repo

@app.route("/")
def home():
    return "Trade Validation API Running"

@app.route("/validate", methods=["POST"])
def validate():

    try:
        ce_data = request.json.get("ce_data")
        pe_data = request.json.get("pe_data")
        index_data = request.json.get("index_data")

        if not ce_data or not pe_data or not index_data:
            return jsonify({"error": "Missing JSON data"}), 400

        output_folder = run_validation(ce_data, pe_data, index_data)

        upload_folder_to_github(
            folder_path=output_folder,
            repo=GITHUB_REPO,
            token=GITHUB_TOKEN
        )

        return jsonify({
            "status": "success",
            "message": "Validation complete & uploaded to GitHub"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()