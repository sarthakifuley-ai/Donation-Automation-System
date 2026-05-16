import requests

WHATSAPP_SERVICE_URL = "http://localhost:3001"


def send_whatsapp(phone, message):
    """
    Sends a WhatsApp message via the local whatsapp-web.js service.
    The service must be running: cd whatsapp-service && node index.js
    """
    try:
        print(f"[whatsapp] Sending to {phone} via {WHATSAPP_SERVICE_URL}/send ...")

        response = requests.post(
            f"{WHATSAPP_SERVICE_URL}/send",
            json={"phone": phone, "message": message},
            timeout=30
        )

        print(f"[whatsapp] HTTP {response.status_code} - raw: {response.text[:200]}")

        result = response.json()

        if result.get("success"):
            print(f"[whatsapp] ✅ Message sent to {phone}")
            return True
        else:
            print(f"[whatsapp] ❌ Failed to send to {phone}: {result.get('error')}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"[whatsapp] ❌ WhatsApp service is not running at {WHATSAPP_SERVICE_URL}!")
        print(f"[whatsapp]    Start it with: cd whatsapp-service && node index.js")
        return False
    except Exception as e:
        print(f"[whatsapp] ❌ Unexpected error sending to {phone}: {e}")
        return False


def is_whatsapp_ready():
    """Check if the WhatsApp service is running and logged in."""
    try:
        response = requests.get(f"{WHATSAPP_SERVICE_URL}/status", timeout=5)
        ready = response.json().get("ready", False)
        print(f"[whatsapp] Status check: ready={ready}")
        return ready
    except Exception as e:
        print(f"[whatsapp] Status check failed: {e}")
        return False
