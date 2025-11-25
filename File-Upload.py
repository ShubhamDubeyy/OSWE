from flask import Flask, request, make_response, send_from_directory
import threading, time, requests, os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# -------------------- FLASK SERVER --------------------

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = "wiener"
PASSWORD = "peter"

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
        resp = make_response("Logged in")
        resp.set_cookie("session", "1")
        return resp
    return "Invalid", 401

@app.route("/upload", methods=["POST"])
def upload():
    if request.cookies.get("session") != "1":
        return "Not logged in", 403
    f = request.files.get("file")
    if not f:
        return "No file", 400
    f.save(os.path.join(UPLOAD_FOLDER, f.filename))
    return f"/uploads/{f.filename}"

@app.route("/uploads/<path:name>")
def serve_file(name):
    return send_from_directory(UPLOAD_FOLDER, name)

def run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False)

# -------------------- CLIENT CALLBACK --------------------

if __name__ == "__main__":
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(1)  # wait for server to start

    BASE = "http://127.0.0.1:5000"
    s = requests.Session()
    s.verify = False
    s.proxies = {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080"
    }

    print("Logging in...")
    r = s.post(BASE + "/login", data={"username": "wiener", "password": "peter"})
    print("[+] Login status:", r.status_code)

    print("\n[*] Uploading test.html...")
    with open("test.html", "rb") as f:
        r = s.post(BASE + "/upload", files={"file": ("test.html", f, "text/html")})

    print("[+] Upload status:", r.status_code)
    uploaded_path = r.text.strip()
    print("[+] File stored at:", uploaded_path)

    print("\n[*] Calling back uploaded file...")
    r = s.get(BASE + uploaded_path)
    print("[+] Callback status:", r.status_code)
    print("[+] File content:\n")
    print(r.text)
