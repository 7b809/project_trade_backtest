from flask import Flask, request, jsonify
import os, requests, shutil
from validator import run_validation
from github_uploader import upload_folder_to_github
from dotenv import load_dotenv
from github_uploader import (
    upload_folder_to_github,
    delete_folder_recursive,
    get_folder_contents
)
from utils.fetch_json import fetch_github_json

from flask import render_template
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

@app.route("/health")
def home():
    return "Trade Validation API Running"


@app.route("/")
def ui():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
# ==========================================
# DELETE ONE FOLDER
# ==========================================

@app.route("/delete/<folder_name>", methods=["DELETE"])
def delete_one(folder_name):

    try:
        full_path = f"validation_results/{folder_name}"

        delete_folder_recursive(
            repo=GITHUB_REPO,
            token=GITHUB_TOKEN,
            folder_path=full_path
        )

        return jsonify({
            "status": "success",
            "deleted_folder": folder_name
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# DELETE ALL FOLDERS
# ==========================================

@app.route("/delete-all", methods=["GET"])
def delete_all():

    try:
        base_path = "validation_results"

        delete_folder_recursive(
            repo=GITHUB_REPO,
            token=GITHUB_TOKEN,
            folder_path=base_path
        )

        return jsonify({
            "status": "success",
            "message": "All validation folders deleted"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# VALIDATE ROUTE
# ==========================================

@app.route("/validate", methods=["POST"])
def validate():

    output_folder = None

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
        # RUN VALIDATION
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
        # BUILD RAW URLS
        # ==========================

        raw_base = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"
        raw_urls = [raw_base + path for path in uploaded_files]

        # Find matched signals file
        matched_signals_url = next(
            (raw_base + p for p in uploaded_files if "matched_signals.xlsx" in p),
            None
        )

        folder_path = f"validation_results/validation_{timestamp}"
        folder_url = f"https://github.com/{GITHUB_REPO}/tree/main/{folder_path}"

        response_data = {
            "status": "success",
            "repo": GITHUB_REPO,
            "folder_path": folder_path,
            "folder_url": folder_url,
            "matched_signals_url": matched_signals_url,
            "files": raw_urls
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if output_folder and os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            
            
# ==========================================
# VALIDATE FROM GITHUB JSON FILES
# ==========================================
# ==========================================
# VALIDATE FROM GITHUB JSON FILES
# ==========================================

@app.route("/validate-from-github", methods=["POST"])
def validate_from_github():

    output_folder = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        ce_url = data.get("ce_url")
        pe_url = data.get("pe_url")
        index_url = data.get("index_url")

        if not ce_url or not pe_url or not index_url:
            return jsonify({"error": "Missing GitHub raw URLs"}), 400

        # ==========================
        # FETCH RAW JSON SAFELY
        # ==========================

        ce_data = fetch_github_json(ce_url, "CE")
        pe_data = fetch_github_json(pe_url, "PE")
        index_data = fetch_github_json(index_url, "INDEX")

        # ==========================
        # RUN VALIDATION
        # ==========================

        output_folder = run_validation(ce_data, pe_data, index_data)

        # ==========================
        # UPLOAD RESULTS TO GITHUB
        # ==========================

        uploaded_files, timestamp = upload_folder_to_github(
            folder_path=output_folder,
            repo=GITHUB_REPO,
            token=GITHUB_TOKEN
        )

        # ==========================
        # BUILD RAW URLS
        # ==========================

        raw_base = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"
        raw_urls = [raw_base + path for path in uploaded_files]

        matched_signals_url = next(
            (raw_base + p for p in uploaded_files if "matched_signals.xlsx" in p),
            None
        )

        folder_path = f"validation_results/validation_{timestamp}"
        folder_url = f"https://github.com/{GITHUB_REPO}/tree/main/{folder_path}"

        response_data = {
            "status": "success",
            "repo": GITHUB_REPO,
            "folder_path": folder_path,
            "folder_url": folder_url,
            "matched_signals_url": matched_signals_url,
            "files": raw_urls
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if output_folder and os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            
# ==========================================
# LIST ALL VALIDATION FOLDERS
# ==========================================

@app.route("/list-validations", methods=["GET"])
def list_validations():

    try:
        base_path = "validation_results"

        contents = get_folder_contents(
            repo=GITHUB_REPO,
            token=GITHUB_TOKEN,
            path=base_path
        )

        folders = [
            item["name"]
            for item in contents
            if item["type"] == "dir"
        ]

        return jsonify({
            "status": "success",
            "repo": GITHUB_REPO,
            "folders": folders
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
                
# ==========================================
# RUN LOCAL SERVER
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)