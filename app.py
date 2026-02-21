from flask import Flask, request, jsonify
import os
from validator import run_validation
from github_uploader import upload_folder_to_github
from dotenv import load_dotenv
import shutil

from github_uploader import delete_folder_recursive
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
    
@app.route("/delete-all", methods=["DELETE"])
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

    output_folder = None  # define outside try

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

        raw_urls = [
            f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{path}"
            for path in uploaded_files
        ]

        folder_url = f"https://github.com/{GITHUB_REPO}/tree/main/validation_results/validation_{timestamp}"

        response_data = {
            "status": "success",
            "folder_url": folder_url,
            "files": raw_urls
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # ==========================
        # CLEANUP LOCAL FILES
        # ==========================

        if output_folder and os.path.exists(output_folder):
            shutil.rmtree(output_folder)

# ==========================================
# RUN LOCAL SERVER
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)