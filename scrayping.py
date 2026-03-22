import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = "https://doraeiga.com/2026/dora26manga/jpg/{:04d}.jpg"
save_dir = "images"
max_workers = 5
retry_limit = 3

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
}

os.makedirs(save_dir, exist_ok=True)

failed = []

def download(i):
    url = base_url.format(i)
    filename = os.path.join(save_dir, f"{i:04d}.jpg")

    if os.path.exists(filename):
        print(f"[{i:04d}] Skip")
        return True

    for attempt in range(retry_limit):
        try:
            print(f"[{i:04d}] Downloading... (try {attempt+1})")
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()

            with open(filename, "wb") as f:
                f.write(res.content)

            time.sleep(0.5)
            return True

        except requests.exceptions.RequestException as e:
            print(f"[{i:04d}] Error: {e}")
            time.sleep(1)

    return False

# 並列ダウンロード
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(download, i): i for i in range(1, 37)}

    for future in as_completed(futures):
        i = futures[future]
        if not future.result():
            failed.append(i)

# 再試行フェーズ
if failed:
    print("\n--- Retry Failed Downloads ---")
    retry_failed = []

    for i in failed:
        if not download(i):
            retry_failed.append(i)

    if retry_failed:
        print("\nStill failed:", retry_failed)
    else:
        print("\nAll retries succeeded!")

else:
    print("\nAll downloads succeeded!")