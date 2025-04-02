from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os, json

app = Flask(__name__)

# Google Drive API 設定
SERVICE_ACCOUNT_FILE = "path/to/your/https://drive.google.com/uc?export=download&amp;id=1P7wTb5gi3UiDwZCoMSP-kZMPLK2ZUzns"  # サービスアカウントJSONファイルのパス
FOLDER_ID = "your_google_drive_folder_id"  # Google DriveのフォルダID

credentials = service_account.Credentials.from_service_account_file("https://drive.google.com/uc?export=download&amp;id=1P7wTb5gi3UiDwZCoMSP-kZMPLK2ZUzns")

drive_service = build("drive", "v3", credentials=credentials)

# お問い合わせデータ保存用 (JSON ファイル)
CONTACTS_FILE = "contacts.json"
LINKS_FILE = "links.json"


def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "ファイルが見つかりません", 400

    file = request.files["file"]
    filename = file.filename
    file_path = os.path.join("temp", filename)
    file.save(file_path)

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file_drive = drive_service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    os.remove(file_path)

    return jsonify({"message": "アップロード成功", "file_id": file_drive["id"], "link": file_drive["webViewLink"]})


@app.route("/contact", methods=["POST"])
def save_contact():
    data = request.json
    contacts = load_json(CONTACTS_FILE)
    contacts.append({"name": data["name"], "message": data["message"]})
    save_json(CONTACTS_FILE, contacts)
    return jsonify({"message": "お問い合わせを受け付けました"})


@app.route("/videos", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return "動画ファイルが見つかりません", 400

    file = request.files["video"]
    filename = file.filename
    file_path = os.path.join("temp", filename)
    file.save(file_path)

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file_drive = drive_service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    os.remove(file_path)

    return jsonify({"message": "動画アップロード成功", "video_id": file_drive["id"], "link": file_drive["webViewLink"]})


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    app.run(debug=True)
