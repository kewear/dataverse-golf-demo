# Dataverse Workspace

## Environment
- **URL:** https://org1a892f71.crm.dynamics.com/
- **Solution:** GolfCourseAgent
- **Publisher Prefix:** 
- **PAC Auth Profile:** nonprod

## Repo Layout
- `/solutions/GolfCourseAgent/` — unpacked solution source files (source of truth)
- `/plugins/` — C# Dataverse plugin projects
- `/.dataverse/` — plugin skills, scripts, and templates (committed, no credentials)
- `.env` — local environment config (not committed, gitignored)
- `.vscode/settings.json` — MCP server config (not committed, gitignored)

## Workflows

**Pull from environment to repo:**
```
pac solution export --name GolfCourseAgent --path ./solutions/GolfCourseAgent.zip --managed false
pac solution unpack --zipfile ./solutions/GolfCourseAgent.zip --folder ./solutions/GolfCourseAgent
rm ./solutions/GolfCourseAgent.zip
git add ./solutions/GolfCourseAgent && git commit -m "chore: pull GolfCourseAgent" && git push
```

**Push from repo to environment:**
```
pac solution pack --zipfile ./solutions/GolfCourseAgent.zip --folder ./solutions/GolfCourseAgent
pac solution import --path ./solutions/GolfCourseAgent.zip --environment https://org1a892f71.crm.dynamics.com/ --async --activate-plugins
rm ./solutions/GolfCourseAgent.zip
```

**Validate after push (using Python SDK):**

```python
from PowerPlatform.Dataverse.client import DataverseClient
from scripts.auth import get_credential, load_env
import os

load_env()
client = DataverseClient(base_url=os.environ["DATAVERSE_URL"], credential=get_credential())

# Check table exists
info = client.tables.get("<logical_name>")
print(f"[{'PASS' if info else 'FAIL'}] Table '<logical_name>'")

# Check import errors
pages = client.records.get("msdyn_solutionhistory", filter="msdyn_status eq 1",
    select=["msdyn_name", "msdyn_exceptionmessage"], orderby=["msdyn_starttime desc"], top=5)
errors = [e for page in pages for e in page]
print(f"[{'FAIL' if errors else 'PASS'}] {len(errors)} failed import(s)")
```

## Metadata Conventions
- Table prefix: `_` (from `.env`; also visible in `solutions/GolfCourseAgent/Other/Solution.xml`)
- All GUIDs in form and view XML must be unique — generate with `python -c "import uuid; print(str(uuid.uuid4()).upper())"`
- Business rules are stored as JSON in `Entities/<table>/Workflows/`

## C# Plugins
- Projects live in `/plugins/<PluginName>/`
- All assemblies must be strong-named (`.snk` key file, gitignored)
- Register via `scripts/register_plugin.py` (first time) or `pac plugin push --pluginId` (updates)
- See `/plugins/README.md` for the full build and registration steps
