"""Download per-ayah timing for each reciter from mp3quran.net and save one compact JSON file per reciter.

Output: data/timing/<key>.json  ->  {"<surah>": [[ayah, start_ms, end_ms], ...], ...}
"""
import json
import os
import time
import urllib.request

READS = {"alafasy": 123, "minshawi": 112, "binhumaid": 137}
API = "https://mp3quran.net/api/v3/ayat_timing?surah={s}&read={r}"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "timing")
os.makedirs(OUT, exist_ok=True)


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "adhkar-maha/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print("retry", url, e)
            time.sleep(2 * (i + 1))
    return None


for key, rid in READS.items():
    data = {}
    for s in range(1, 115):
        rows = get(API.format(s=s, r=rid))
        if isinstance(rows, list) and rows:
            data[str(s)] = [[int(x["ayah"]), int(x["start_time"]), int(x["end_time"])] for x in rows]
        time.sleep(0.2)
    with open(os.path.join(OUT, f"{key}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    print(key, "surahs with timing:", len(data))
