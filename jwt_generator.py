import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Konfigurasi
MAX_RETRIES = 5
MAX_WORKERS = 15
API_URL_TEMPLATE = "https://jwt-generate-danssrmdn.vercel.app/token?uid={uid}&password={password}"

INPUT_FILE = "uid_bd.json"      # daftar akun UID + password
OUTPUT_FILE = "token_bd.json"   # hasil generate token

def fetch_token(account):
    uid = account.get("uid")
    password = account.get("password")

    if not uid or not password:
        print(f"❌ Invalid account entry: {account}")
        return None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            url = API_URL_TEMPLATE.format(uid=uid, password=password)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if token:
                    print(f"[{uid}] ✅ Token generated.")
                    return {"uid": uid, "token": token}
                else:
                    print(f"[{uid}] ⚠️ No token in response.")
            else:
                print(f"[{uid}] ⚠️ Status code: {response.status_code}")
        except Exception as e:
            print(f"[{uid}] ⚠️ Error (attempt {attempt}): {e}")

        time.sleep(0.5)  # delay antar retry

    print(f"[{uid}] ❌ Failed after {MAX_RETRIES} retries.")
    return None

def main():
    try:
        with open(INPUT_FILE, "r") as f:
            accounts = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {INPUT_FILE}: {e}")
        return

    tokens = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(fetch_token, acc) for acc in accounts]
        for future in as_completed(futures):
            result = future.result()
            if result:
                tokens.append(result)

    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(tokens, f, indent=4)
        print(f"✅ All tokens saved to {OUTPUT_FILE}.")
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")

if __name__ == "__main__":
    main()
