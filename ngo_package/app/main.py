import os
import sys
import json
import time
import hashlib
import hmac
import secrets
import subprocess
import pandas as pd
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.whatsapp import is_whatsapp_ready

app = FastAPI()
watch_process = None
is_sending = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(BASE_DIR, "data", "users.json")
SESSIONS_FILE = os.path.join(BASE_DIR, "data", "sessions.json")

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"{salt}:{hashed.hex()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split(":")
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
        return hmac.compare_digest(check.hex(), hashed)
    except:
        return False

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_sessions() -> dict:
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE) as f:
        return json.load(f)

def save_sessions(sessions: dict):
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def create_session(username: str) -> str:
    token = secrets.token_urlsafe(32)
    sessions = load_sessions()
    sessions[token] = {"username": username, "created_at": time.time()}
    save_sessions(sessions)
    return token

def get_current_user(request: Request) -> str:
    token = request.headers.get("X-Auth-Token", "")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sessions = load_sessions()
    session = sessions.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    if time.time() - session["created_at"] > 8 * 3600:
        del sessions[token]
        save_sessions(sessions)
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    return session["username"]

@app.post("/auth/register")
async def register(request: Request):
    data = await request.json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    if not username or not password or not full_name:
        return {"status": "error", "message": "All fields are required."}
    if len(username) < 3:
        return {"status": "error", "message": "Username must be at least 3 characters."}
    if len(password) < 6:
        return {"status": "error", "message": "Password must be at least 6 characters."}
    users = load_users()
    if username in users:
        return {"status": "error", "message": "Username already exists. Please choose another."}
    users[username] = {
        "full_name": full_name,
        "password_hash": hash_password(password),
        "created_at": time.time()
    }
    save_users(users)
    token = create_session(username)
    return {"status": "success", "token": token, "username": username, "full_name": full_name}

@app.post("/auth/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    users = load_users()
    user = users.get(username)
    if not user or not verify_password(password, user["password_hash"]):
        return {"status": "error", "message": "Incorrect username or password."}
    token = create_session(username)
    return {"status": "success", "token": token, "username": username, "full_name": user["full_name"]}

@app.post("/auth/logout")
async def logout(request: Request):
    token = request.headers.get("X-Auth-Token", "")
    sessions = load_sessions()
    if token in sessions:
        del sessions[token]
        save_sessions(sessions)
    return {"status": "success", "message": "Logged out."}

@app.get("/auth/me")
async def me(username: str = Depends(get_current_user)):
    users = load_users()
    user = users.get(username, {})
    return {"username": username, "full_name": user.get("full_name", username)}

@app.get("/whatsapp-qr")
def whatsapp_qr(username: str = Depends(get_current_user)):
    try:
        import requests as req
        response = req.get("http://localhost:3001/qr", timeout=5)
        return response.json()
    except:
        return {"qr": None, "ready": is_whatsapp_ready()}

@app.get("/whatsapp-status")
def whatsapp_status(username: str = Depends(get_current_user)):
    return {"ready": is_whatsapp_ready()}

@app.post("/session/stop")
async def stop_session(username: str = Depends(get_current_user)):
    global watch_process
    if watch_process:
        watch_process.terminate()
        watch_process = None
    return {"status": "success", "message": "Session stopped."}

def get_school_file(school_name):
    safe = school_name.strip().replace("/", "-").replace("\\", "-")
    return os.path.join(DATA_DIR, f"{safe}.xlsx")

def get_school_df(school_name):
    try:
        return pd.read_excel(get_school_file(school_name))
    except:
        return pd.DataFrame(columns=["student_name","class","school","parent_name","phone","amount","date"])

def save_school_df(school_name, df):
    path = get_school_file(school_name)
    temp = path.replace(".xlsx", "_temp.xlsx")
    df.to_excel(temp, index=False)
    os.replace(temp, path)

@app.get("/")
def home():
    return {"message": "NGO Donation Chatbot Running"}

@app.get("/schools")
def list_schools(username: str = Depends(get_current_user)):
    schools = []
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith(".xlsx") and not f.endswith("_temp.xlsx"):
            schools.append(f.replace(".xlsx", ""))
    return {"schools": schools}

@app.post("/schools/create")
async def create_school(request: Request, username: str = Depends(get_current_user)):
    data = await request.json()
    name = data.get("school_name", "").strip()
    if not name:
        return {"status": "error", "message": "School name cannot be empty."}
    path = get_school_file(name)
    if os.path.exists(path):
        return {"status": "exists", "message": f"'{name}' already exists."}
    df = pd.DataFrame(columns=["student_name","class","school","parent_name","phone","amount","date"])
    df.to_excel(path, index=False)
    return {"status": "created", "message": f"'{name}' created successfully."}

@app.get("/total-donation")
def total_donation(school: str = "", username: str = Depends(get_current_user)):
    if school:
        df = get_school_df(school)
        return {"total": int(df["amount"].sum()) if len(df) > 0 else 0, "school": school}
    total = 0
    for f in os.listdir(DATA_DIR):
        if f.endswith(".xlsx") and not f.endswith("_temp.xlsx"):
            try:
                total += int(pd.read_excel(os.path.join(DATA_DIR, f))["amount"].sum())
            except:
                pass
    return {"total": total, "school": "all"}

@app.get("/donation-stats")
def donation_stats(school: str = "", username: str = Depends(get_current_user)):
    if school:
        df = get_school_df(school)
    else:
        frames = []
        for f in os.listdir(DATA_DIR):
            if f.endswith(".xlsx") and not f.endswith("_temp.xlsx"):
                try:
                    frames.append(pd.read_excel(os.path.join(DATA_DIR, f)))
                except:
                    pass
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["amount"])

    n = len(df)
    avg = round(float(df["amount"].mean()), 2) if n > 0 else 0
    mx = int(df["amount"].max()) if n > 0 else 0
    monthly, yearly = [], []

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        v = df.dropna(subset=["date"])
        if len(v) > 0:
            for p, a in v.groupby(v["date"].dt.to_period("M"))["amount"].sum().items():
                monthly.append({"label": p.strftime("%b %Y"), "amount": int(a)})
            for y, a in v.groupby(v["date"].dt.year)["amount"].sum().items():
                yearly.append({"label": str(y), "amount": int(a)})

    if not monthly and n > 0:
        chunk = max(1, n // 6)
        for i in range(0, n, chunk):
            monthly.append({"label": f"Batch {i//chunk+1}", "amount": int(df.iloc[i:i+chunk]["amount"].sum())})

    return {"total_donors": n, "avg_donation": avg, "max_donation": mx, "monthly": monthly, "yearly": yearly}

@app.post("/send-broadcast")
async def send_broadcast(request: Request, username: str = Depends(get_current_user)):
    global is_sending
    if is_sending:
        return {"status": "Already sending. Please wait."}
    if not is_whatsapp_ready():
        return {"status": "❌ WhatsApp is not connected. Please scan the QR code first."}
    is_sending = True
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        school = data.get("school", "").strip()
        if not message:
            return {"status": "No message provided."}
        if not school:
            return {"status": "Please select a school before broadcasting."}
        school_file = get_school_file(school)
        if not os.path.exists(school_file):
            return {"status": f"No data file found for '{school}'."}
        result = subprocess.run(
            [sys.executable, "scripts/broadcast.py", message, school_file],
            cwd=BASE_DIR
        )
        if result.returncode == 0:
            return {"status": f"✅ Broadcast complete to {school}!"}
        else:
            return {"status": "⚠️ Broadcast finished with errors."}
    except Exception as e:
        return {"status": f"Error: {str(e)}"}
    finally:
        is_sending = False

@app.post("/add-donation")
async def add_donation(request: Request, username: str = Depends(get_current_user)):
    data = await request.json()
    school = data.get("school_file", "").strip()
    if not school:
        return {"status": "No school selected."}
    df = get_school_df(school)
    new_row = {
        "student_name": data.get("student_name", ""),
        "class": data.get("class", ""),
        "school": school,
        "parent_name": data.get("parent_name", ""),
        "phone": data.get("phone", ""),
        "amount": int(data.get("amount", 0)),
        "date": data.get("donation_date", "")
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_school_df(school, df)
    # Send thank-you in background — capture output to a log for debugging
    log_path = os.path.join(BASE_DIR, "broadcast_log.txt")
    with open(log_path, "a") as log_out:
        subprocess.Popen(
            [sys.executable, "scripts/send_thankyou.py",
             str(data.get("phone", "")),
             str(data.get("parent_name", "")),
             str(data.get("student_name", "")),
             str(data.get("school", school)),   # use display school name from form
             str(data.get("amount", 0))],
            cwd=BASE_DIR,
            stdout=log_out,
            stderr=log_out
        )
    return {"status": f"Donation added successfully to {school}!"}

@app.post("/start_watch")
def start_watch(username: str = Depends(get_current_user)):
    global watch_process
    if watch_process is None:
        watch_process = subprocess.Popen([sys.executable, "scripts/watch_excel.py"], cwd=BASE_DIR)
    return {"status": "Excel watcher started"}

@app.get("/recent-donations")
def recent_donations(school: str = "", limit: int = 10, username: str = Depends(get_current_user)):
    if not school:
        return {"rows": []}
    df = get_school_df(school)
    if len(df) == 0:
        return {"rows": []}
    df = df.tail(limit).iloc[::-1]
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "student_name": str(row.get("student_name", "")),
            "parent_name": str(row.get("parent_name", "")),
            "class": str(row.get("class", "")),
            "amount": row.get("amount", 0),
            "date": str(row.get("date", ""))
        })
    return {"rows": rows}

@app.get("/stop_watch")
def stop_watch(username: str = Depends(get_current_user)):
    global watch_process
    if watch_process:
        watch_process.terminate()
        watch_process = None
    return {"status": "Excel watcher stopped"}
