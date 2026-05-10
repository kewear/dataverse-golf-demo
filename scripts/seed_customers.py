"""Seed 100 golf customers: 50 members (with linked memberships) and 50 non-members."""
import sys, os, random, uuid
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.auth import get_credential, load_env
from PowerPlatform.Dataverse.client import DataverseClient

load_env()
client = DataverseClient(base_url=os.environ["DATAVERSE_URL"], credential=get_credential())

# Name pools
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
    "Dennis", "Maria", "Jerry", "Heather",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]

random.seed(42)

def random_email(first, last):
    domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com", "hotmail.com"]
    return f"{first.lower()}.{last.lower()}{random.randint(1,99)}@{random.choice(domains)}"

def random_phone():
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"

# Generate unique name combinations
used_names = set()
def get_unique_name():
    while True:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full = f"{first} {last}"
        if full not in used_names:
            used_names.add(full)
            return first, last, full

# ============================================================
# Create 50 memberships first
# ============================================================
print("Creating 50 memberships...")
membership_ids = []
today = datetime.now()

for i in range(50):
    first, last, full = get_unique_name()
    # Most memberships are active, a few expired or suspended
    if i < 40:
        status = 100000000  # Active
        start = today - timedelta(days=random.randint(30, 365))
        end = today + timedelta(days=random.randint(30, 365))
    elif i < 45:
        status = 100000001  # Expired
        start = today - timedelta(days=random.randint(400, 730))
        end = today - timedelta(days=random.randint(1, 60))
    else:
        status = 100000002  # Suspended
        start = today - timedelta(days=random.randint(60, 365))
        end = today + timedelta(days=random.randint(30, 180))

    membership_name = f"MEM-{i+1:04d}"
    record = client.records.create("zava_membership", {
        "zava_name": membership_name,
        "zava_status": status,
        "zava_startdate": start.strftime("%Y-%m-%d"),
        "zava_enddate": end.strftime("%Y-%m-%d"),
    })
    membership_ids.append((record, full, first, last))
    if (i + 1) % 10 == 0:
        print(f"  {i+1}/50 memberships created")

print(f"  ✅ 50 memberships created\n")

# ============================================================
# Create 50 member customers (linked to memberships)
# ============================================================
print("Creating 50 member customers...")
for i, (mem_id, full, first, last) in enumerate(membership_ids):
    record = client.records.create("zava_customer", {
        "zava_name": full,
        "zava_email": random_email(first, last),
        "zava_phone": random_phone(),
        "zava_customer_membership@odata.bind": f"/zava_memberships({mem_id})",
    })
    if (i + 1) % 10 == 0:
        print(f"  {i+1}/50 member customers created")

print(f"  ✅ 50 member customers created\n")

# ============================================================
# Create 50 non-member customers (no membership link)
# ============================================================
print("Creating 50 non-member customers...")
for i in range(50):
    first, last, full = get_unique_name()
    record = client.records.create("zava_customer", {
        "zava_name": full,
        "zava_email": random_email(first, last),
        "zava_phone": random_phone(),
    })
    if (i + 1) % 10 == 0:
        print(f"  {i+1}/50 non-member customers created")

print(f"  ✅ 50 non-member customers created\n")

print("🎉 Done! 100 customers created (50 members, 50 non-members)")
