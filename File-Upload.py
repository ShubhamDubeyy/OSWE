import threading, time, requests, os
from flask import Flask, request, make_response, send_from_directory
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# ============================================
#  FLASK SERVER (LOGIN → UPLOAD → SERVE FILE)
# ============================================

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

    path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(path)

    return f"/files/{f.filename}"

@app.route("/files/<path:name>")
def serve_file(name):
    return send_from_directory(UPLOAD_DIR, name)

def run_server():
    app.run(host="127.0.0.1", port=5000, debug=False)


# ============================================
#  CLIENT (LOGIN → UPLOAD LOCAL FILE → CALLBACK)
# ============================================

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE = "http://127.0.0.1:5000"
LOGIN = BASE + "/login"
UPLOAD = BASE + "/upload"

LOCAL_FILE = "test.html"                    # <-- your local file
PROXIES = {"http":"http://127.0.0.1:8080",  # <-- for Burp
           "https":"http://127.0.0.1:8080"}

s = requests.Session()
s.verify = False
s.proxies = PROXIES


if __name__ == "__main__":

    # Start Flask server in background
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(1)  # wait for server to boot

    # 1) Login
    print("[*] Logging in...")
    r = s.post(LOGIN, data={"username":"wiener","password":"peter"})
    print("[+] Login status:", r.status_code)

    # 2) Upload local file
    print("\n[*] Uploading:", LOCAL_FILE)
    with open(LOCAL_FILE, "rb") as f:
        r = s.post(UPLOAD, files={"file": (LOCAL_FILE, f, "text/html")})

    print("[+] Upload response:", r.text)
    file_path = r.text.strip()
    file_url = BASE + file_path

    # 3) Callback (fetch file from server)
    print("\n[*] Callback:", file_url)
    r = s.get(file_url)
    print("[+] Callback status:", r.status_code)
    print("[+] File content:\n")
    print(r.text)
