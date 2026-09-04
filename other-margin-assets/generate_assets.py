#!/usr/bin/env python3
# generate_assets.py - batch driver for the Seedream pipeline (text-to-image + local download)
# Usage:
#   python generate_assets.py anchor "prompt"
#   python generate_assets.py batch manifest.json
import sys, os, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = r"C:\Users\ANMS\.openclaw-autoclaw\skills\autoglm-generate-image-seedream\generate-image-seedream.py"

def gen(prompt):
    r = subprocess.run([sys.executable, SKILL, prompt], capture_output=True, text=True, encoding="utf-8", timeout=240)
    out = r.stdout.strip()
    if not out:
        raise RuntimeError("empty output: " + r.stderr[:400])
    data = json.loads(out)
    if data.get("code") != 0 or not data.get("data", {}).get("image_url"):
        raise RuntimeError("bad response: " + json.dumps(data)[:400])
    return data["data"]["image_url"]

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(path, "wb") as f:
        f.write(resp.read())
    return os.path.getsize(path)

def one(asset_id, prompt):
    url = gen(prompt)
    ext = ".png"
    path = os.path.join(HERE, asset_id + ext)
    size = download(url, path)
    print(f"OK {asset_id} {size//1024}KB {url}")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "anchor":
        one(sys.argv[2], sys.argv[3])
    else:
        with open(os.path.join(HERE, "batch.json"), encoding="utf-8") as f:
            items = json.load(f)
        for it in items:
            try:
                one(it["id"], it["prompt"])
            except Exception as e:
                print(f"FAIL {it['id']} {e}")
