"""Turn a Eurostat API response (JSON-stat 2.0) into flat rows. Standard library only.

    rows = eurostat_rows("isoc_eb_ai", indic_is="E_AI_TANY", size_emp="GE10",
                         unit="PC_ENT", nace_r2="C10-S951_X_K", sinceTimePeriod="2025")
    # -> [{'geo': 'DK', 'geo_label': 'Denmark', 'time': '2025', ..., 'value': 42.03, 'flag': None}, ...]
"""
import json
import urllib.parse
import urllib.request

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


def eurostat_rows(dataset: str, **filters) -> list[dict]:
    url = API + dataset + "?" + urllib.parse.urlencode({"format": "JSON", "lang": "EN", **filters})
    with urllib.request.urlopen(url, timeout=60) as resp:
        d = json.load(resp)
    ids, sizes = d["id"], d["size"]
    # category index -> code, per dimension
    codes = {k: {i: c for c, i in d["dimension"][k]["category"]["index"].items()} for k in ids}
    labels = d["dimension"]["geo"]["category"]["label"]
    flags = d.get("status", {})
    rows = []
    for key, value in d["value"].items():          # values are keyed by a flat index (sparse)
        k, row = int(key), {}
        for dim, size in reversed(list(zip(ids, sizes))):   # row-major: last dimension changes fastest
            row[dim] = codes[dim][k % size]
            k //= size
        row["geo_label"] = labels.get(row["geo"])
        row["value"] = value
        row["flag"] = flags.get(key)                 # e.g. 'p' provisional, 'e' estimated, 'b' break in series
        rows.append(row)
    return rows


if __name__ == "__main__":
    for r in sorted(eurostat_rows("isoc_ec_ib20", indic_is="I_BLT12", ind_type="IND_TOTAL",
                                  unit="PC_IND", sinceTimePeriod="2025"), key=lambda r: -r["value"])[:5]:
        print(r["geo"], r["value"], r["flag"])
