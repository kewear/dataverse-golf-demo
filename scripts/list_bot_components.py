"""List bot components for the Golf Booking Agent."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.auth import get_token, load_env
import requests, json

load_env()
BASE_URL = os.environ["DATAVERSE_URL"].rstrip("/")
BOT_ID = "3d8ba7ca-136c-4b2b-9457-71ae35560c10"

headers = {
    "Authorization": f"Bearer {get_token()}",
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
}

resp = requests.get(
    f"{BASE_URL}/api/data/v9.2/botcomponents?$filter=_parentbotid_value eq {BOT_ID}&$select=name,componenttype,schemaname,data",
    headers=headers
)
components = resp.json().get("value", [])
print(f"Found {len(components)} components:\n")
for c in components:
    data_str = c.get("data") or ""
    print(f"  Type: {c.get('componenttype')} | Schema: {c.get('schemaname')}")
    if "gpt" in (c.get("schemaname") or "").lower() or c.get("componenttype") == 6:
        print(f"  DATA: {data_str[:500]}")
    print()
