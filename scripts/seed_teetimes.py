"""Seed tee-time slots and bookings for Friday May 8, 2026 at ~70% occupancy."""
import sys, os, random
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.auth import get_credential, load_env
from PowerPlatform.Dataverse.client import DataverseClient

load_env()
client = DataverseClient(base_url=os.environ["DATAVERSE_URL"], credential=get_credential())

TARGET_DATE = "2026-05-08"
START_MINUTE = 420   # 7:00 AM
END_MINUTE = 1020    # 5:00 PM (last tee time)
INTERVAL = 10
MAX_PLAYERS = 4
OCCUPANCY = 0.70

random.seed(2026)

# ============================================================
# Generate all tee-time slots for the day
# ============================================================
print(f"Creating tee-time slots for {TARGET_DATE} (7:00 AM - 5:00 PM, every 10 min)...")

slots = []
minute = START_MINUTE
while minute <= END_MINUTE:
    hour = minute // 60
    mins = minute % 60
    ampm = "AM" if hour < 12 else "PM"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0:
        display_hour = 12
    display_time = f"{display_hour}:{mins:02d} {ampm}"
    slot_name = f"{TARGET_DATE} {display_time}"

    record_id = client.records.create("zava_teetime", {
        "zava_name": slot_name,
        "zava_date": TARGET_DATE,
        "zava_time": minute,
        "zava_displaytime": display_time,
        "zava_maxplayers": MAX_PLAYERS,
        "zava_currentplayers": 0,
        "zava_isavailable": True,
    })
    slots.append({"id": record_id, "minute": minute, "display": display_time, "players": 0})
    minute += INTERVAL

print(f"  ✅ {len(slots)} tee-time slots created\n")

# ============================================================
# Get all customers and rate info
# ============================================================
print("Loading customers and rates...")

customers_member = []
customers_guest = []
for page in client.records.get("zava_customer", select=["zava_customerid", "zava_name", "_zava_customer_membership_value"]):
    for r in page:
        if r.get("_zava_customer_membership_value"):
            customers_member.append(r)
        else:
            customers_guest.append(r)

print(f"  Members: {len(customers_member)}, Guests: {len(customers_guest)}")

# Get memberships for status lookup
memberships = {}
for page in client.records.get("zava_membership", select=["zava_membershipid", "zava_status", "zava_startdate", "zava_enddate"]):
    for r in page:
        memberships[r["zava_membershipid"]] = r

# Get rates
rates = {}
for page in client.records.get("zava_rate", select=["zava_rateid", "zava_startminute", "zava_endminute", "zava_amount"]):
    for r in page:
        rates[r["zava_rateid"]] = r

rate_list = list(rates.values())
print(f"  Rates loaded: {len(rate_list)}")

def get_rate_for_minute(minute):
    for r in rate_list:
        if r["zava_startminute"] <= minute <= r["zava_endminute"]:
            return r
    return rate_list[-1]  # fallback to off-peak

def is_good_standing(membership_id):
    if not membership_id:
        return False
    mem = memberships.get(membership_id)
    if not mem:
        return False
    return mem["zava_status"] == 100000000  # Active

# ============================================================
# Create bookings at ~70% occupancy
# ============================================================
total_capacity = len(slots) * MAX_PLAYERS
target_bookings = int(total_capacity * OCCUPANCY)
print(f"\nTotal capacity: {total_capacity} spots across {len(slots)} slots")
print(f"Target bookings (~70%): {target_bookings}")
print(f"Creating bookings...")

# Distribute bookings across slots (not uniform — some full, some partial, some empty)
# Create a weighted distribution
slot_fills = []
for slot in slots:
    # Random fill: 0-4 players per slot, weighted toward 3-4
    fill = random.choices([0, 1, 2, 3, 4], weights=[5, 10, 15, 35, 35])[0]
    slot_fills.append(fill)

# Adjust to hit ~70% target
current_total = sum(slot_fills)
while current_total > target_bookings + 5:
    idx = random.randint(0, len(slot_fills) - 1)
    if slot_fills[idx] > 0:
        slot_fills[idx] -= 1
        current_total -= 1
while current_total < target_bookings - 5:
    idx = random.randint(0, len(slot_fills) - 1)
    if slot_fills[idx] < 4:
        slot_fills[idx] += 1
        current_total += 1

# Mix of members (40%) and guests (60%) in bookings
all_customers = customers_member + customers_guest
booking_count = 0

for i, slot in enumerate(slots):
    num_players = slot_fills[i]
    if num_players == 0:
        continue

    # Pick random customers for this slot
    slot_customers = random.sample(all_customers, min(num_players, len(all_customers)))

    for cust in slot_customers:
        cust_id = cust["zava_customerid"]
        cust_name = cust["zava_name"]
        mem_id = cust.get("_zava_customer_membership_value")
        is_member = mem_id is not None
        good_standing = is_good_standing(mem_id)

        rate = get_rate_for_minute(slot["minute"])
        if is_member and good_standing:
            amount = 0
        else:
            amount = rate["zava_amount"]

        booking_name = f"{cust_name} - {TARGET_DATE} {slot['display']}"

        booking_data = {
            "zava_name": booking_name,
            "zava_booking_customer@odata.bind": f"/zava_customers({cust_id})",
            "zava_booking_teetime@odata.bind": f"/zava_teetimes({slot['id']})",
            "zava_booking_rate@odata.bind": f"/zava_rates({rate['zava_rateid']})",
            "zava_ismember": is_member,
            "zava_isingoodstanding": good_standing,
            "zava_amountcharged": amount,
            "zava_status": 100000000,  # Confirmed
            "zava_bookedon": "2026-05-06T10:00:00Z",
        }

        if mem_id:
            booking_data["zava_booking_membership@odata.bind"] = f"/zava_memberships({mem_id})"

        client.records.create("zava_booking", booking_data)
        booking_count += 1

    # Update the tee-time slot with current players and availability
    client.records.update("zava_teetime", slot["id"], {
        "zava_currentplayers": num_players,
        "zava_isavailable": num_players < MAX_PLAYERS,
    })

    if (i + 1) % 10 == 0:
        print(f"  Processed {i+1}/{len(slots)} slots ({booking_count} bookings so far)")

print(f"\n✅ {booking_count} bookings created across {len(slots)} tee-time slots")
print(f"   Occupancy: {booking_count}/{total_capacity} = {booking_count/total_capacity*100:.1f}%")

# Summary stats
full_slots = sum(1 for f in slot_fills if f == 4)
empty_slots = sum(1 for f in slot_fills if f == 0)
partial_slots = len(slots) - full_slots - empty_slots
print(f"   Full slots (4/4): {full_slots}")
print(f"   Partial slots: {partial_slots}")
print(f"   Empty slots: {empty_slots}")
