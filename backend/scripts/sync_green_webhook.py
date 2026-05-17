import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND_DIR / ".env"
NGROK_API = "http://127.0.0.1:4040/api/tunnels"
WEBHOOK_PATH = "/webhook/whatsapp/"


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def request_json(url: str, method: str = "GET", payload: dict | None = None, timeout: int = 20) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def wait_for_ngrok_url() -> str:
    for attempt in range(1, 31):
        try:
            tunnels = request_json(NGROK_API, timeout=3).get("tunnels", [])
            https_urls = [
                tunnel.get("public_url", "")
                for tunnel in tunnels
                if tunnel.get("proto") == "https" and tunnel.get("public_url", "").startswith("https://")
            ]
            if https_urls:
                return https_urls[0].rstrip("/")
        except Exception:
            pass

        print(f"[sync] waiting for ngrok tunnel... {attempt}/30")
        time.sleep(2)

    raise RuntimeError("ngrok tunnel was not found on http://127.0.0.1:4040")


def green_url(base_url: str, instance_id: str, method: str, token: str) -> str:
    return f"{base_url.rstrip('/')}/waInstance{instance_id}/{method}/{token}"


def main() -> int:
    env = {**load_env(ENV_PATH), **os.environ}

    instance_id = env.get("GREEN_API_INSTANCE_ID", "")
    token = env.get("GREEN_API_TOKEN", "")
    base_url = env.get("GREEN_API_BASE_URL", "https://api.green-api.com")

    if not instance_id or not token:
        print("[sync] ERROR: GREEN_API_INSTANCE_ID or GREEN_API_TOKEN is missing in backend/.env")
        return 2

    public_url = wait_for_ngrok_url()
    webhook_url = f"{public_url}{WEBHOOK_PATH}"

    print(f"[sync] ngrok public url: {public_url}")
    print(f"[sync] webhook url: {webhook_url}")
    print(f"[sync] green instance: {instance_id}")

    state = request_json(green_url(base_url, instance_id, "getStateInstance", token))
    print(f"[sync] green state: {state.get('stateInstance', 'unknown')}")

    payload = {
        "webhookUrl": webhook_url,
        "webhookUrlToken": "",
        "incomingWebhook": "yes",
        "outgoingWebhook": "no",
        "outgoingMessageWebhook": "yes",
        "outgoingAPIMessageWebhook": "yes",
        "markIncomingMessagesReaded": "no",
        "markIncomingMessagesReadedOnReply": "yes",
    }
    result = request_json(green_url(base_url, instance_id, "setSettings", token), "POST", payload)
    print(f"[sync] setSettings: {result}")
    print("[sync] Green API applies settings within up to 5 minutes.")

    for attempt in range(1, 11):
        settings = request_json(green_url(base_url, instance_id, "getSettings", token))
        current = settings.get("webhookUrl", "")
        print(f"[sync] verify {attempt}/10: {current}")
        if current == webhook_url:
            print("[sync] OK: Green API webhook points to current ngrok URL.")
            return 0
        time.sleep(15)

    print("[sync] WARNING: Green API accepted settings but still reports the old webhook.")
    print("[sync] Wait 1-5 minutes or check the Green API cabinet if it does not change.")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        print(f"[sync] HTTP ERROR {exc.code}: {details}")
        raise SystemExit(1)
    except Exception as exc:
        print(f"[sync] ERROR: {exc}")
        raise SystemExit(1)
