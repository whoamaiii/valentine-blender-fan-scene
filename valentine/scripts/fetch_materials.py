"""Download the small, source-recorded Poly Haven material set for this scene."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "textures"
UA = {"User-Agent": "ValentineBlenderFanScene/1.0"}
manifest = []
jobs = []
for asset in ("rough_wood", "brown_mud", "mud_forest"):
    req = urllib.request.Request(f"https://api.polyhaven.com/files/{asset}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as response:
        metadata = json.load(response)
    for channel in ("Diffuse", "nor_gl", "Rough", "Displacement"):
        info = metadata[channel]["2k"]["jpg"]
        name = f"{asset}_{channel}.jpg"
        jobs.append((name, info))
        manifest.append({"asset": asset, "channel": channel, "file": name,
                         "source": f"https://polyhaven.com/a/{asset}", "license": "CC0",
                         "resolution": "2k", **info})


def fetch(job):
    name, info = job
    target = DEST / name
    if target.exists() and hashlib.md5(target.read_bytes()).hexdigest() == info["md5"]:
        return name
    req = urllib.request.Request(info["url"], headers=UA)
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
    assert len(data) == info["size"] and hashlib.md5(data).hexdigest() == info["md5"], name
    target.write_bytes(data)
    return name


DEST.mkdir(parents=True, exist_ok=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for name in pool.map(fetch, jobs):
        print("VERIFIED", name, flush=True)
(DEST / "SOURCES.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("TOTAL_BYTES", sum(job[1]["size"] for job in jobs))
