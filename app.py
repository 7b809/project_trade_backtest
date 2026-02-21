from flask import Flask, request, jsonify
import os
from validator import run_validation
from github_uploader import upload_folder_to_github
from dotenv import load_dotenv

# ==========================================
# LOAD ENV VARIABLES
# ==========================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():
    return "Trade Validation API Running"


# ==========================================
# VALIDATE ROUTE
# ==========================================

@app.route("/validate", methods=["POST"])
def validate():

    # Optional API Key Security
    if API_KEY:
        if request.headers.get("x-api-key") != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        ce_data = data.get("ce_data")
        pe_data = data.get("pe_data")
        index_data = data.get("index_data")

        if not ce_data or not pe_data or not index_data:
            return jsonify({"error": "Missing JSON data"}), 400

        # ==========================
        # RUN VALIDATION ENGINE
        # ==========================

        output_folder = run_validation(ce_data, pe_data, index_data)

        # ==========================
        # UPLOAD TO GITHUB
        # ==========================

        uploaded_files, timestamp = upload_folder_to_github(
            folder_path=output_folder,
            repo=GITHUB_REPO,
            token=GITHUB_TOKEN
        )

        # ==========================
        # GENERATE RAW FILE URLS
        # ==========================

        raw_urls = [
            f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{path}"
            for path in uploaded_files
        ]

        folder_url = f"https://github.com/{GITHUB_REPO}/tree/main/validation_results/validation_{timestamp}"

        # ==========================
        # FINAL RESPONSE
        # ==========================

        return jsonify({
            "status": "success",
            "folder_url": folder_url,
            "files": raw_urls
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# RUN LOCAL SERVER
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)