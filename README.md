# Dataverse Golf Demo

A demo Dataverse solution built with **GitHub Copilot CLI** and the **Dataverse MCP server**, showcasing how to build a complete golf course booking system using natural language.

## What's Included

### Dataverse Solution (`solutions/GolfCourseAgent/`)
- **Golf Membership** — Tracks membership records with status (Active/Expired/Suspended)
- **Golf Customer** — Customer contact info linked to memberships
- **Golf Rate** — Time-based pricing (Peak/Off-Peak)
- **Tee Time** — Available tee time slots
- **Tee Time Booking** — Booking records linking customers, tee times, rates, and memberships
- **Zava Golf Booking Agent** — Copilot Studio agent for natural language booking

### Helper Scripts (`scripts/`)
Python scripts for authentication, table creation, data seeding, and agent management.

## Importing the Solution

1. Go to [Power Apps Maker Portal](https://make.powerapps.com)
2. Navigate to **Solutions** > **Import Solution**
3. Upload `solutions/GolfCourseAgent.zip` (export it first — see below)
4. Follow the import wizard

Or use PAC CLI:
```bash
pac solution pack --zipfile ./solutions/GolfCourseAgent.zip --folder ./solutions/GolfCourseAgent
pac solution import --path ./solutions/GolfCourseAgent.zip --activate-plugins
```

## Data Model

```
Golf Membership <── Golf Customer <── Tee Time Booking ──> Tee Time
       ^                                    |
       └────────────────────────────────────└──> Golf Rate
```

## Built With
- [GitHub Copilot CLI](https://github.com/features/copilot)
- [Dataverse MCP Server](https://www.npmjs.com/package/@microsoft/dataverse)
- [PAC CLI](https://aka.ms/PowerPlatformCLI)

## License
MIT
