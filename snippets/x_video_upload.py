"""Post a video to X (Twitter) with the official API from Python.

Chunked media upload (INIT / APPEND / FINALIZE / STATUS) + POST /2/tweets.
Needs OAuth 1.0a user-context keys in environment variables:
X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET

    pip install requests requests_oauthlib
    python x_video_upload.py clip.mp4 "Text of the post"
"""
import os
import sys
import time

import requests
from requests_oauthlib import OAuth1

UPLOAD = "https://upload.x.com/1.1/media/upload.json"
TWEETS = "https://api.x.com/2/tweets"
CHUNK = 4 * 1024 * 1024  # 4 MB per APPEND

auth = OAuth1(os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
              os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"])


def upload_video(path: str) -> str:
    size = os.path.getsize(path)
    r = requests.post(UPLOAD, auth=auth, timeout=60, data={
        "command": "INIT", "total_bytes": size,
        "media_type": "video/mp4", "media_category": "tweet_video"})
    r.raise_for_status()
    media_id = r.json()["media_id_string"]

    with open(path, "rb") as f:
        index = 0
        while chunk := f.read(CHUNK):
            r = requests.post(UPLOAD, auth=auth, timeout=120,
                              data={"command": "APPEND", "media_id": media_id, "segment_index": index},
                              files={"media": chunk})
            r.raise_for_status()  # APPEND answers 2xx with an empty body
            index += 1

    r = requests.post(UPLOAD, auth=auth, timeout=60, data={"command": "FINALIZE", "media_id": media_id})
    r.raise_for_status()
    info = r.json().get("processing_info")

    # Videos are transcoded asynchronously: poll until "succeeded" or "failed".
    while info and info["state"] in ("pending", "in_progress"):
        time.sleep(info.get("check_after_secs", 5))
        r = requests.get(UPLOAD, auth=auth, timeout=60, params={"command": "STATUS", "media_id": media_id})
        r.raise_for_status()
        info = r.json().get("processing_info")
        print("processing:", info)
    if info and info["state"] == "failed":
        raise RuntimeError(f"X could not process the video: {info.get('error')}")
    return media_id


def post_with_video(path: str, text: str) -> str:
    media_id = upload_video(path)
    r = requests.post(TWEETS, auth=auth, timeout=60,
                      json={"text": text, "media": {"media_ids": [media_id]}})
    r.raise_for_status()
    return r.json()["data"]["id"]


if __name__ == "__main__":
    tweet_id = post_with_video(sys.argv[1], sys.argv[2])
    print(f"https://x.com/i/status/{tweet_id}")
