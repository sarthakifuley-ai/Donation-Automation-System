import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.whatsapp import send_whatsapp, is_whatsapp_ready

if len(sys.argv) < 6:
    print("Usage: send_thankyou.py <phone> <parent_name> <student_name> <school> <amount>")
    sys.exit(1)

phone        = sys.argv[1].strip()
parent_name  = sys.argv[2].strip()
student_name = sys.argv[3].strip()
school       = sys.argv[4].strip()
amount       = sys.argv[5].strip()

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sent_log.txt")

# ── Clean phone number ──────────────────────────────────────────────────────
# Remove all non-digit characters first
phone_digits = "".join(c for c in phone if c.isdigit())

# Remove trailing .0 if came from Excel float
if phone_digits.endswith("0") and len(phone_digits) > 10:
    try:
        phone_digits = str(int(float(phone))).replace(".0", "")
        phone_digits = "".join(c for c in phone_digits if c.isdigit())
    except:
        pass

# Normalize to 10-digit Indian mobile number, then add 91 prefix
if len(phone_digits) == 10:
    phone_clean = "91" + phone_digits
elif len(phone_digits) == 12 and phone_digits.startswith("91"):
    phone_clean = phone_digits
elif len(phone_digits) == 11 and phone_digits.startswith("0"):
    phone_clean = "91" + phone_digits[1:]
else:
    phone_clean = phone_digits  # use as-is and hope for the best

phone_with_plus = "+" + phone_clean

print(f"[send_thankyou] Phone raw='{phone}' → cleaned='{phone_with_plus}'")

# ── Check WhatsApp is ready ─────────────────────────────────────────────────
if not is_whatsapp_ready():
    print(f"[send_thankyou] ❌ WhatsApp service is not ready. Cannot send to {phone_with_plus}")
    sys.exit(1)

# ── Check if already sent ───────────────────────────────────────────────────
try:
    with open(LOG_FILE, "r") as f:
        sent_numbers = set(line.strip() for line in f.readlines())
except:
    sent_numbers = set()

if phone_with_plus in sent_numbers:
    print(f"[send_thankyou] Thank-you already sent to {phone_with_plus}. Skipping.")
    sys.exit(0)

# ── Build message ───────────────────────────────────────────────────────────
message = (
    f"Respected {parent_name} \U0001f44b We sincerely thank you for your constant encouragement and support.\n"
    f"{student_name} from {school}, as a proud Child A Change Maker, has contributed \u20b9{amount} — "
    f"creating a meaningful impact in the lives of less privileged communities we work with, at Yuva Rural Association.\n"
    f"Your support inspires us to continue this journey, and we look forward to your continued encouragement "
    f"for our Child A Change Maker program and YUVA Rural Association.\n"
    f"Together, we can create lasting change.\n\n"
    f"\U0001f310 Learn more about us: https://yraindia.org/"
)

# ── Send ────────────────────────────────────────────────────────────────────
print(f"[send_thankyou] Sending thank-you to {phone_with_plus}...")

try:
    success = send_whatsapp(phone_with_plus, message)
except Exception as e:
    print(f"[send_thankyou] ❌ Exception while sending: {e}")
    traceback.print_exc()
    sys.exit(1)

if success:
    with open(LOG_FILE, "a") as f:
        f.write(phone_with_plus + "\n")
    print(f"[send_thankyou] ✅ Thank-you sent and logged for {phone_with_plus}")
else:
    print(f"[send_thankyou] ❌ Failed to send thank-you to {phone_with_plus}")
    sys.exit(1)
