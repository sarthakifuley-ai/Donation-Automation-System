import sys
import os
import hashlib
import pandas as pd
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.whatsapp import send_whatsapp

if len(sys.argv) < 3:
    print("Usage: broadcast.py <message> <excel_file_path>")
    sys.exit(1)

message    = sys.argv[1]
EXCEL_FILE = sys.argv[2]
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BROADCAST_LOG = os.path.join(BASE_DIR, "broadcast_log.txt")

# Unique hash per message — same msg never sent twice to same number,
# new message always goes to everyone again
message_hash = hashlib.md5(message.encode()).hexdigest()[:10]

try:
    df = pd.read_excel(EXCEL_FILE)
except Exception as e:
    print(f"Error reading Excel file: {e}")
    sys.exit(1)

phones = df["phone"].dropna().tolist()

try:
    with open(BROADCAST_LOG, "r") as f:
        already_sent = set(f.read().splitlines())
except:
    already_sent = set()

school_name = os.path.basename(EXCEL_FILE).replace(".xlsx", "")
print(f"Starting broadcast to {len(phones)} contacts in '{school_name}'...")
print(f"Message ID: {message_hash}")

sent_count = 0
skip_count = 0
fail_count = 0
seen_this_run = set()

for phone in phones:
    phone = str(phone).strip().replace("+", "").replace(" ", "").replace(".0", "")
    while phone.startswith("91") and len(phone) > 10:
        phone = phone[2:]
    if len(phone) == 10:
        phone = "91" + phone
    phone = "+" + phone

    log_key = f"{message_hash}|{phone}"

    if log_key in already_sent:
        print(f"⏭️  Already sent this message to {phone}, skipping.")
        skip_count += 1
        continue

    if phone in seen_this_run:
        print(f"⏭️  Duplicate number, skipping {phone}.")
        skip_count += 1
        continue

    print(f"📤 Sending to {phone}...")
    success = send_whatsapp(phone, message)

    if success:
        with open(BROADCAST_LOG, "a") as f:
            f.write(log_key + "\n")
        already_sent.add(log_key)
        seen_this_run.add(phone)
        sent_count += 1
    else:
        fail_count += 1

    time.sleep(2)

print(f"✅ Broadcast done! Sent: {sent_count} | Skipped: {skip_count} | Failed: {fail_count}")
