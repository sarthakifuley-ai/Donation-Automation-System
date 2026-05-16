# How to Run — YUVA NGO Staff Portal

## Quick Start

### Step 1 — First time only: Run `SETUP.bat`
Double-click `SETUP.bat`. It will:
- Check Python and Node.js are installed
- Automatically detect and use Microsoft Edge (built into Windows 10/11)
- Clear any broken browser cache from previous attempts
- Install all Python and Node packages

> **Important:** When installing Python, tick **"Add Python to PATH"**

### Step 2 — Every time: Run `START.bat`
Double-click `START.bat`. It will:
- Start the WhatsApp service (Node.js window)
- Start the Python server (Python window)
- Open the website in your browser automatically

---

## Manual Start (if START.bat doesn't work)

Open **two** Command Prompt windows in the project folder.

### Window 1 — WhatsApp Service
```
cd whatsapp-service
node index.js
```

### Window 2 — Python Server
```
python -m uvicorn app.main:app --reload
```

### Open the Website
Open `frontend/index.html` in your browser, or go to http://localhost:8000

---

## Connecting WhatsApp

1. After logging in, click **"Connect WhatsApp"** at the top
2. A QR code will appear on screen
3. On your phone: WhatsApp → Menu (⋮) → Linked Devices → Link a Device
4. Scan the QR code
5. Status will change to ✅ Connected

> After scanning once, WhatsApp stays connected even after restarting.

---

## Stopping the App

Double-click `STOP.bat` — it closes all windows cleanly.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Could not find Chrome` | Run `SETUP.bat` — it auto-detects Edge and clears broken cache |
| `uvicorn is not recognized` | Use `python -m uvicorn ...` (fixed in START.bat) |
| `pip is not recognized` | Use `python -m pip install ...` (fixed in START.bat) |
| Python packages missing | Run `SETUP.bat` again |
| Node packages missing | Run `SETUP.bat` again |
| Port 8000 already in use | Run `STOP.bat` first, then `START.bat` |
| WhatsApp QR not showing | Wait 10 seconds and refresh the page |
