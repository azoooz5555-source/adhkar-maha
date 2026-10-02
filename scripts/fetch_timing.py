"""Download per-ayah timing for each reciter from mp3quran.net and save one compact JSON file per reciter.

Output: data/timing/<key>.json  ->  {"<surah>": [[ayah, start_ms, end_ms], ...], ...}
"""
import json
import os
import time
import urllib.request

READS = {"alafasy": 123, "minshawi": 112}
# Quran.com (QuranicAudio) recitations: key -> recitation id. Audio files are the ones that match these timings.
QDC = {"basit": 2}
QDC_API = "https://api.qurancdn.com/api/qdc/audio/reciters/{r}/audio_files?chapter={s}&segments=true"
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


for key, rid in QDC.items():
    data, urls = {}, {}
    for s in range(1, 115):
        j = get(QDC_API.format(s=s, r=rid))
        files = (j or {}).get("audio_files") or []
        if files:
            f0 = files[0]
            urls[str(s)] = f0.get("audio_url")
            rows = []
            for t in f0.get("verse_timings") or []:
                a = int(str(t["verse_key"]).split(":")[1])
                rows.append([a, int(t["timestamp_from"]), int(t["timestamp_to"])])
            if rows:
                data[str(s)] = rows
        time.sleep(0.2)
    with open(os.path.join(OUT, f"{key}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    with open(os.path.join(OUT, f"{key}_urls.json"), "w", encoding="utf-8") as f:
        json.dump(urls, f, separators=(",", ":"))
    print(key, "surahs with timing:", len(data), "urls:", len(urls), "sample:", urls.get("1"))
