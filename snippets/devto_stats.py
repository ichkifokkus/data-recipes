"""Pull your own dev.to article stats and group them by title pattern and tag.

    export DEVTO_API_KEY=...   (dev.to -> Settings -> Extensions -> DEV Community API Keys)
    python devto_stats.py
"""
import collections
import datetime as dt
import os
import re
import statistics

import requests

API = "https://dev.to/api/articles/me/published"
headers = {"api-key": os.environ["DEVTO_API_KEY"], "User-Agent": "devto-stats/1.0"}

articles, page = [], 1
while True:
    batch = requests.get(API, headers=headers, params={"per_page": 100, "page": page}, timeout=30).json()
    if not batch:
        break
    articles += batch
    page += 1

cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat()
articles = [a for a in articles if a["published_at"] < cutoff]   # give new posts 48 h first


def kind(title: str) -> str:
    t = title.lower()
    if "n8n" in t:
        return "n8n recipe"
    if "how to" in t[:40]:
        return "how-to"
    if re.match(r"^(i|we) ", t):
        return "'I did X' story"
    if "?" in t:
        return "question title"
    return "other"


def report(groups):
    rows = [(k, len(v), statistics.median(a["page_views_count"] for a in v),
             sum(a["public_reactions_count"] for a in v), sum(a["comments_count"] for a in v))
            for k, v in groups.items() if len(v) >= 3]
    for k, n, med, react, comm in sorted(rows, key=lambda r: -r[2]):
        print(f"{k:22} n={n:3}  median views={med:5}  reactions={react:3}  comments={comm:3}")


by_kind, by_tag = collections.defaultdict(list), collections.defaultdict(list)
for a in articles:
    by_kind[kind(a["title"])].append(a)
    for tag in a["tag_list"]:
        by_tag[tag].append(a)

print(f"{len(articles)} articles, {sum(a['page_views_count'] for a in articles)} views\n")
report(by_kind)
print()
report(by_tag)
