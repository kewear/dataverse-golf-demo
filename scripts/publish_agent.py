"""Publish the Golf Booking Agent properly."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.auth import get_token, load_env
import requests, json, time

load_env()
BASE_URL = os.environ["DATAVERSE_URL"].rstrip("/")
BOT_ID = "3d8ba7ca-136c-4b2b-9457-71ae35560c10"

headers = {
    "Authorization": f"Bearer {get_token()}",
    "Content-Type": "application/json",
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
}

# Check current status
resp = requests.get(
    f"{BASE_URL}/api/data/v9.2/bots({BOT_ID})?$select=synchronizationstatus,statuscode,statecode",
    headers=headers
)
data = resp.json()
print(f"Current state: statecode={data.get('statecode')}, statuscode={data.get('statuscode')}")
sync = data.get("synchronizationstatus", "")
print(f"Sync status: {sync[:300]}")

# Try PvaProvision - this actually provisions/publishes the bot
print("\nAttempting PvaProvision...")
resp = requests.post(
    f"{BASE_URL}/api/data/v9.2/bots({BOT_ID})/Microsoft.Dynamics.CRM.PvaProvision",
    headers=headers,
    json={}
)
print(f"PvaProvision: {resp.status_code}")
if resp.text:
    print(resp.text[:300])

# Try changing status to trigger publish
print("\nAttempting status update to trigger publish...")
resp2 = requests.patch(
    f"{BASE_URL}/api/data/v9.2/bots({BOT_ID})",
    headers=headers,
    json={"statecode": 0, "statuscode": 1}
)
print(f"Status update: {resp2.status_code}")

# Wait and check again
time.sleep(5)
resp3 = requests.get(
    f"{BASE_URL}/api/data/v9.2/bots({BOT_ID})?$select=synchronizationstatus",
    headers=headers
)
print(f"\nUpdated sync: {resp3.json().get('synchronizationstatus', '')[:300]}")
