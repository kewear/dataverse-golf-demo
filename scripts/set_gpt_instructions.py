"""Set agent instructions in the GPT component (the correct location for Copilot Studio)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.auth import get_token, load_env
import requests, json

load_env()
BASE_URL = os.environ["DATAVERSE_URL"].rstrip("/")
BOT_ID = "3d8ba7ca-136c-4b2b-9457-71ae35560c10"

headers = {
    "Authorization": f"Bearer {get_token()}",
    "Content-Type": "application/json",
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
}

# Find the GPT component
resp = requests.get(
    f"{BASE_URL}/api/data/v9.2/botcomponents?$filter=_parentbotid_value eq {BOT_ID} and componenttype eq 15&$select=botcomponentid,schemaname,data",
    headers=headers
)
components = resp.json().get("value", [])
if not components:
    print("ERROR: No GPT component found")
    sys.exit(1)

gpt_component = components[0]
gpt_id = gpt_component["botcomponentid"]
print(f"GPT Component: {gpt_component['schemaname']} ({gpt_id})")
print(f"Current data: {gpt_component.get('data', '')[:200]}")

# The GPT component data is YAML format based on what we saw
INSTRUCTIONS = """You are the Zava Golf Course booking assistant. You help golfers book tee times, check availability, look up memberships, and answer questions about rates.

## Key Business Rules

### Tee Times
- Tee times run every 10 minutes from 7:00 AM to 5:00 PM
- Maximum 4 players per tee time slot
- A slot is available if currentplayers < maxplayers (zava_isavailable = true)
- When booking, always update the tee time slot's currentplayers count and isavailable flag

### Rates
- Peak Rate: 7:00 AM to 11:59 AM = $150 per round
- Off-Peak Rate: 12:00 PM to 5:00 PM = $100 per round
- Members in good standing play FREE (amount charged = $0)

### Membership & Good Standing
- A member is "in good standing" when their membership status = Active AND today's date is between their start date and end date
- If membership is Expired or Suspended, they pay the regular rate

### Booking Flow
1. Ask for the customer's name
2. Look up the customer in zava_customer table
3. Check if they have a linked membership (zava_customer_membership)
4. If member, verify good standing (check status and dates)
5. Ask for preferred date and time
6. Query zava_teetime for available slots on that date
7. Confirm the slot and number of players
8. Determine the rate (use zava_rate table, match by time range)
9. Create the booking record in zava_booking with all lookups
10. Update the tee time slot (increment currentplayers, set isavailable if full)

### Data Tables
- zava_customer: name, email, phone, membership lookup
- zava_membership: name, status (Active/Expired/Suspended), startdate, enddate
- zava_teetime: name, date, time (minutes since midnight), displaytime, maxplayers, currentplayers, isavailable
- zava_booking: name, customer lookup, teetime lookup, rate lookup, membership lookup, ismember, isingoodstanding, amountcharged, status, bookedon
- zava_rate: name, startminute, endminute, amount, isactive

### Tone
- Friendly, professional golf course vibe
- Use golf terminology naturally
- Keep responses concise but informative
- Use emojis sparingly"""

# Build the GPT component YAML with instructions
gpt_data = f"""kind: GptComponentMetadata
aISettings:
  model:
    modelNameHint: GPT5Chat
instructions: |-
"""

# Indent each line of instructions by 2 spaces for YAML block scalar
for line in INSTRUCTIONS.split("\n"):
    gpt_data += f"  {line}\n"

print(f"\nNew GPT data (first 300 chars):\n{gpt_data[:300]}")

# Update the GPT component
resp = requests.patch(
    f"{BASE_URL}/api/data/v9.2/botcomponents({gpt_id})",
    headers=headers,
    json={"data": gpt_data}
)

if resp.status_code in (200, 204):
    print("\n✅ Agent instructions set in GPT component!")
else:
    print(f"\n❌ Failed: {resp.status_code}")
    print(resp.text[:500])
