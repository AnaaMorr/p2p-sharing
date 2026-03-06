from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
import os

app = Flask(__name__)

SHARED_FOLDER = "shared_files"
DOWNLOAD_FOLDER = "downloads"

os.makedirs(SHARED_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    files = os.listdir(SHARED_FOLDER)
    downloaded = os.listdir(DOWNLOAD_FOLDER)
    return render_template("index.html", files=files, downloaded=downloaded)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if file and file.filename:
        file.save(os.path.join(SHARED_FOLDER, file.filename))
    return redirect("/")


# Serve shared files (for browser download)
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)


# Serve downloaded files (received from peers)
@app.route("/get-download/<filename>")
def get_download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


# Peer fetches a file from this server over HTTPS
@app.route("/peer/fetch/<filename>")
def peer_fetch(filename):
    path = os.path.join(SHARED_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)


# List files available for peers to fetch
@app.route("/peer/files")
def peer_files():
    files = os.listdir(SHARED_FOLDER)
    return jsonify({"files": files})


# Returns the direct URL so browser downloads straight from peer
@app.route("/peer-download", methods=["POST"])
def peer_download():
    data = request.get_json()
    peer_url = data.get("peer_url", "").strip().rstrip("/")
    filename = data.get("filename", "").strip()

    if not peer_url or not filename:
        return jsonify({"success": False, "error": "Missing peer URL or filename."}), 400

    direct_url = f"{peer_url}/peer/fetch/{filename}"
    return jsonify({"success": True, "direct_url": direct_url})


if __name__ == "__main__":
    app.run(debug=True)