"""Seed rate records."""
import sys, os, requests, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.auth import get_token, load_env
load_env()
BASE = os.environ['DATAVERSE_URL'].rstrip('/')
h = {'Authorization': f'Bearer {get_token()}', 'Content-Type': 'application/json', 'MSCRM.SolutionName': 'ZavaGolfBookings'}

rates = [
    {'zava_name': 'Peak Rate', 'zava_startminute': 420, 'zava_endminute': 720, 'zava_amount': 150.0, 'zava_isactive': True},
    {'zava_name': 'Off-Peak Rate', 'zava_startminute': 720, 'zava_endminute': 1020, 'zava_amount': 100.0, 'zava_isactive': True}
]
for rate in rates:
    r = requests.post(BASE + '/api/data/v9.2/zava_rates', headers=h, json=rate)
    print(f"Rate {rate['zava_name']}: {r.status_code}")
    if r.status_code not in (200, 201, 204):
        print(r.text[:200])
print('✅ Rates seeded')
