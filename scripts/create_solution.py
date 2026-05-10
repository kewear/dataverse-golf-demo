"""Create the ZavaGolfBookings solution in Dataverse."""
from PowerPlatform.Dataverse.client import DataverseClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.auth import get_credential, load_env
import os

load_env()
client = DataverseClient(base_url=os.environ["DATAVERSE_URL"], credential=get_credential())

# Get the publisher ID for 'zava'
pages = client.records.get("publisher", filter="uniquename eq 'zava'", select=["publisherid"])
publisher = None
for page in pages:
    for r in page:
        publisher = r
        break

if not publisher:
    raise Exception("Publisher 'zava' not found")

print(f"Publisher ID: {publisher['publisherid']}")

# Create the solution
sol = client.records.create("solution", {
    "uniquename": "ZavaGolfBookings",
    "friendlyname": "Zava Golf Bookings",
    "version": "1.0.0.0",
    "publisherid@odata.bind": f"/publishers({publisher['publisherid']})"
})
print(f"Solution created: {sol}")
