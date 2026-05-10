"""Check DLP policies affecting our environment."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.auth import load_env
from azure.identity import InteractiveBrowserCredential
import requests

load_env()
tid = os.environ['TENANT_ID']
my_env = 'eb0d7f09-bdfd-4f7a-82d8-902a5d13babf'

cred = InteractiveBrowserCredential(tenant_id=tid)
tok = cred.get_token('https://api.bap.microsoft.com/.default').token
h = {'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'}

r = requests.get('https://api.bap.microsoft.com/providers/PowerPlatform.Governance/v2/policies', headers=h)
data = r.json()

print(f"Total policies in tenant: {len(data['value'])}")
print(f"\nLooking for policies affecting env: {my_env}\n")

matches = []
for p in data['value']:
    pdef = p['policyDefinition']
    env_type = pdef.get('environmentType', '')
    # Match if AllEnvironments or ExceptEnvironments (applies unless excluded) or specifically includes our env
    if env_type == 'AllEnvironments':
        matches.append(pdef)
    elif env_type == 'ExceptEnvironments':
        excluded = [e.get('name') for e in pdef.get('environments', [])]
        if my_env not in excluded:
            matches.append(pdef)
    elif env_type == 'OnlyEnvironments':
        included = [e.get('name') for e in pdef.get('environments', [])]
        if my_env in included:
            matches.append(pdef)

print(f"Policies affecting your environment: {len(matches)}")
for pdef in matches:
    print(f"\n  Policy: {pdef['displayName']}")
    print(f"  ID: {pdef['name']}")
    print(f"  Type: {pdef['environmentType']}")
    print(f"  Created by: {pdef.get('createdBy', {}).get('displayName', '?')}")
    print(f"  Last modified: {pdef.get('lastModifiedTime', '?')}")

# Now get connector details for matching policies
if matches:
    print("\n\n--- Connector Classifications ---")
    for pdef in matches:
        pid = pdef['name']
        print(f"\nPolicy: {pdef['displayName']} ({pid})")
        # Get connector details
        url = f"https://api.bap.microsoft.com/providers/PowerPlatform.Governance/v2/policies/{pid}/connectors"
        cr = requests.get(url, headers=h)
        if cr.status_code == 200:
            connectors = cr.json().get('value', [])
            business = [c for c in connectors if c.get('defaultActionRuleBehavior') == 'Allow' or c.get('classification') == 'Confidential']
            non_business = [c for c in connectors if c.get('classification') == 'General']
            blocked = [c for c in connectors if c.get('classification') == 'Blocked']
            
            # Show all connectors grouped
            groups = {}
            for c in connectors:
                grp = c.get('classification', 'Unknown')
                groups.setdefault(grp, []).append(c.get('displayName', c.get('id', '?')))
            
            for grp, names in groups.items():
                print(f"  [{grp}]: {len(names)} connectors")
                for n in names[:10]:
                    print(f"    - {n}")
                if len(names) > 10:
                    print(f"    ... and {len(names)-10} more")
        else:
            print(f"  Could not fetch connectors: {cr.status_code}")
            # Try alternate format
            url2 = f"https://api.bap.microsoft.com/providers/PowerPlatform.Governance/v2/policies/{pid}"
            cr2 = requests.get(url2, headers=h)
            if cr2.status_code == 200:
                full = cr2.json()
                groups = full.get('connectorGroups', full.get('policyDefinition', {}).get('connectorGroups', []))
                if groups:
                    for g in groups:
                        cls = g.get('classification', '?')
                        conns = g.get('connectors', [])
                        print(f"  [{cls}]: {len(conns)} connectors")
                        for c in conns[:10]:
                            print(f"    - {c.get('name', c.get('id', '?'))}")
                        if len(conns) > 10:
                            print(f"    ... and {len(conns)-10} more")
