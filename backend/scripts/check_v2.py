import json
import urllib.request


def get(url: str):
    return json.loads(urllib.request.urlopen(url, timeout=30).read().decode())


print("health", get("http://127.0.0.1:8000/api/health"))
ov = get("http://127.0.0.1:8000/api/dashboard/overview")
print("dash", ov.get("today_revenue"), ov.get("score"), ov.get("menu_counts"), len(ov.get("diagnosis") or []))
menu = get("http://127.0.0.1:8000/api/menu-analysis")
print("menu", menu["counts"], "n", len(menu["items"]))
rev = get("http://127.0.0.1:8000/api/revenue-analysis")
print("rev worst", rev["worst_day"]["date"], rev["worst_day"]["revenue"], "anomaly", rev["is_anomaly"])
tab = get("http://127.0.0.1:8000/api/table-efficiency")
print("peak", tab["peak"])
print("ok")
