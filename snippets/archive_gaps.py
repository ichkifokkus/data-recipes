"""Find missing days in a daily snapshot archive (archive/<source>/<YYYY-MM-DD>.json.gz).

    python archive_gaps.py path/to/archive [--alert-after 3]

Prints, per source: days present, missing days, and the current failure streak.
Exits with code 1 if any source has been missing for --alert-after days in a row,
so a scheduler or CI job can turn a silent gap into a loud failure.
"""
import argparse
import datetime as dt
import pathlib
import sys


def days(start: dt.date, end: dt.date):
    while start <= end:
        yield start
        start += dt.timedelta(days=1)


def scan(root: pathlib.Path, today: dt.date):
    report = {}
    for src in sorted(p for p in root.iterdir() if p.is_dir()):
        have = {dt.date.fromisoformat(f.name[:10]) for f in src.glob("*.json.gz")}
        if not have:
            continue
        missing = [d for d in days(min(have), today) if d not in have]
        streak = 0
        for d in sorted(days(min(have), today), reverse=True):
            if d in have:
                break
            streak += 1
        report[src.name] = {"present": len(have), "missing": missing, "streak": streak,
                            "last_ok": max(have)}
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--alert-after", type=int, default=3)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    a = ap.parse_args()
    rep = scan(pathlib.Path(a.root), dt.date.fromisoformat(a.today))
    alert = False
    print(f"{'source':26} {'present':>7} {'missing':>7} {'streak':>6}  last ok")
    for name, r in rep.items():
        flag = "  <-- ALERT" if r["streak"] >= a.alert_after else ""
        alert |= bool(flag)
        print(f"{name:26} {r['present']:>7} {len(r['missing']):>7} {r['streak']:>6}  {r['last_ok']}{flag}")
    sys.exit(1 if alert else 0)
