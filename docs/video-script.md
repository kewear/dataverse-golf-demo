# Golf Course Booking Agent — Video Script

## Video Overview

**Title:** Building a Golf Course Booking Agent with Dataverse MCP + Copilot Studio  
**Format:** Two-part walkthrough  
**Environment:** `https://<yourinstance>.crm.dynamics.com/`

---

# PART 1: Building the Solution

---

## Scene 1 — Introduction (2-3 min)

### What to say:

> "Hey everyone — today I'm going to show you how to build a complete golf course booking system using AI-assisted development. We'll use the Dataverse plugin for coding agents inside of GitHub Copilot to create our entire data model through natural language, and then we'll wire it up to a conversational agent in Microsoft Copilot Studio."
>
> "By the end of this video, we'll have a working AI agent that can check tee time availability, look up membership status, handle pricing, and book tee times — all built from scratch."
>
> "Let's get started."

### What to show:

- Your terminal / VS Code workspace open
- The Dataverse MCP plugin configured and visible

---

## Scene 2 — Connect to Dataverse (2-3 min)

### What to say:

> "First, let's make sure we're connected to our Dataverse environment. The Dataverse MCP plugin lets Copilot talk directly to Dataverse — so we can create tables, add columns, query data, all from right here in the terminal."
>
> "Let me verify we're connected."


Connect to https://<yourinstance>.crm.dynamics.com/


### Prompt 1 — List existing tables

```
List the tables in my Dataverse environment
```

**Expected result:** The `list_tables` tool runs and returns existing system/default tables. This proves connectivity.

### What to say after:

> "We're connected. You can see the default system tables. Now let's start building our golf course data model."

---

## Scene 3 — Create the Solution (1-2 min)

### What to say:

> "In Dataverse, every customization lives inside a solution. Think of it as a container that packages all your tables, columns, and relationships together so you can move them between environments. Let's create one."

### Prompt 2 — Create solution

```
Create a new Dataverse solution called "GolfCourseAgent"
```

**Expected result:** Solution is created in the environment.

### What to say after:

> "Our solution is created. Everything we build from here will live inside this solution."

---

## Scene 4 — Create the Membership Table (3-4 min)

### What to say:

> "Let's start with our data model. We're building a golf course booking system, so we need to think about the core entities. First up — memberships. Our golf course has members who get to play for free as long as their membership is active and in good standing."

### Prompt 3 — Create Membership table

```
Create a table called "Golf Membership" with these columns:
- Membership Name (primary name column, string, max 100 characters)
- Status (choice field with options: Active, Expired, Suspended)
- Start Date (date only)
- End Date (date only)

Add this table to the GolfCourseAgent solution.
```

**Expected result:** The `create_table` tool runs and creates the `Golf Membership` table with all four columns.

### Prompt 4 — Verify the table

```
Describe the Golf Membership table so I can verify the columns
```

**Expected result:** The `describe_table` tool returns the schema showing all columns and their types.

### What to say after:

> "There it is — our membership table with status tracking and date ranges. Notice how I didn't have to click through any forms or write any code. Just described what I wanted in plain English."

---

## Scene 5 — Create the Customer Table (2-3 min)

### What to say:

> "Next, we need customers. These are the people who play at our course — some are members, some are walk-in guests."

### Prompt 5 — Create Customer table

```
Create a table called "Golf Customer" with these columns:
- Full Name (primary name column, string, max 200 characters)
- Email (email format)
- Phone (phone format)

Add it to the GolfCourseAgent solution.
```

**Expected result:** The `create_table` tool creates the `Golf Customer` table.

### What to say after:

> "Simple and clean. We'll link customers to memberships in a moment, but first let's get all our tables created."

---

## Scene 6 — Create the Rate Table (2-3 min)

### What to say:

> "Every golf course has different pricing depending on the time of day. We have a peak rate for morning tee times and an off-peak rate for the afternoon. Let's create a rate table to store that."

### Prompt 6 — Create Rate table

```
Create a table called "Golf Rate" with these columns:
- Rate Name (primary name column, string, max 100 characters)
- Start Minute (integer, 0 to 1440 — represents minutes from midnight)
- End Minute (integer, 0 to 1440)
- Amount (money)
- Is Active (boolean, default true)

Add it to the GolfCourseAgent solution.
```

**Expected result:** The `create_table` tool creates the `Golf Rate` table.

### What to say after:

> "We're using minutes from midnight to represent time ranges — so 420 means 7:00 AM, 720 means noon. This makes it easy for the agent to look up which rate applies to a given tee time."

---

## Scene 7 — Create the Tee Time Table (2-3 min)

### What to say:

> "Now for the heart of the system — tee times. These are the bookable slots. Our course runs 10-minute intervals from 7 AM to 5 PM, with a max of 4 players per slot."

### Prompt 7 — Create Tee Time table

```
Create a table called "Tee Time" with these columns:
- Tee Time Name (primary name column, string, max 100 characters)
- Date (date only)
- Time in Minutes (integer, 0 to 1440)
- Display Time (string, max 20 characters — human-readable like "7:30 AM")
- Max Players (integer, 1 to 4)
- Current Players (integer, 0 to 4)
- Is Available (boolean, default true)

Add it to the GolfCourseAgent solution.
```

**Expected result:** The `create_table` tool creates the `Tee Time` table.

### What to say after:

> "We've got both the raw time in minutes for the agent to do comparisons, and a display time string for human-friendly output. That's a little design trick that makes the agent's responses much more natural."

---

## Scene 8 — Create the Booking Table (2-3 min)

### What to say:

> "Last table — bookings. This is where everything comes together. A booking connects a customer to a tee time, tracks the rate, membership status, and how much they were charged."

### Prompt 8 — Create Booking table

```
Create a table called "Tee Time Booking" with these columns:
- Booking Name (primary name column, string, max 200 characters)
- Is Member (boolean, default false)
- Is In Good Standing (boolean, default false)
- Amount Charged (money)
- Status (choice: Confirmed, Cancelled, No-Show)
- Booked On (datetime)

Add it to the GolfCourseAgent solution.
```

**Expected result:** The `create_table` tool creates the `Tee Time Booking` table.

### What to say after:

> "Five tables created, all through natural language. Now let's connect them with relationships."

---

## Scene 9 — Create Relationships (4-5 min)

### What to say:

> "Right now our tables are standalone. We need lookup columns — these are the foreign keys that connect everything together. Let me walk through each relationship."

### Prompt 9a — Customer → Membership

```
Add a lookup column called "Membership" to the Golf Customer table that references the Golf Membership table
```

> "This links a customer to their membership. Not every customer will have one — guests won't."

### Prompt 9b — Booking → Customer

```
Add a lookup column called "Customer" to the Tee Time Booking table that references the Golf Customer table
```

> "Every booking needs to know who made it."

### Prompt 9c — Booking → Tee Time

```
Add a lookup column called "Tee Time" to the Tee Time Booking table that references the Tee Time table
```

> "And which slot they booked."

### Prompt 9d — Booking → Rate

```
Add a lookup column called "Rate" to the Tee Time Booking table that references the Golf Rate table
```

> "What pricing tier was applied."

### Prompt 9e — Booking → Membership

```
Add a lookup column called "Membership" to the Tee Time Booking table that references the Golf Membership table
```

> "And if they used a membership for the booking, we track that here too."

### What to say after:

> "Five relationships — and our data model is fully connected. Let's verify the whole thing."

---

## Scene 10 — Verify the Data Model (2 min)

### What to say:

> "Let me do a quick sanity check on our data model before we move on."

### Prompt 10a — List custom tables

```
List all the tables in my environment that are part of the GolfCourseAgent solution
```

### Prompt 10b — Verify booking table with all lookups

```
Describe the Tee Time Booking table — show me all columns including the lookups
```

**Expected result:** Shows all columns including the lookup relationships to Customer, Tee Time, Rate, and Membership.

### What to say after:

> "Everything's wired up. Five tables, five relationships. Now let's bring this to life with some data."

---

## Scene 11 — Seed Rate Data (2-3 min)

### What to say:

> "An empty database doesn't demo very well. Let's populate our tables with realistic sample data. We'll start with our rate card."

### Prompt 11a — Create Peak Rate

```
Create a record in the Golf Rate table:
- Rate Name: "Peak Rate"
- Start Minute: 420 (7:00 AM)
- End Minute: 720 (12:00 PM)
- Amount: 150.00
- Is Active: true
```

### Prompt 11b — Create Off-Peak Rate

```
Create another Golf Rate record:
- Rate Name: "Off-Peak Rate"
- Start Minute: 720 (12:00 PM)
- End Minute: 1020 (5:00 PM)
- Amount: 100.00
- Is Active: true
```

### Prompt 11c — Verify rates

```
Show me all records in the Golf Rate table — I want to see the rate name and amount
```

### What to say after:

> "Two rates — $150 for peak morning hours, $100 for the afternoon. Simple pricing structure."

---

## Scene 12 — Seed Membership & Customer Data (4-5 min)

### What to say:

> "Now let's create some memberships and customers. We'll create a mix — some active members, one expired, one suspended, and a few guests with no membership at all."

### Prompt 12a — Create memberships

```
Create 5 records in the Golf Membership table:

1. Name: "MEM-0001", Status: Active, Start Date: 2026-01-01, End Date: 2026-12-31
2. Name: "MEM-0002", Status: Active, Start Date: 2026-03-15, End Date: 2027-03-15
3. Name: "MEM-0003", Status: Active, Start Date: 2025-06-01, End Date: 2026-06-01
4. Name: "MEM-0004", Status: Expired, Start Date: 2025-01-01, End Date: 2025-12-31
5. Name: "MEM-0005", Status: Suspended, Start Date: 2026-02-01, End Date: 2026-08-01
```

### Prompt 12b — Create member customers

```
Create 5 Golf Customer records, each linked to one of the memberships we just created:

1. Full Name: "James Smith", Email: james.smith@gmail.com, Phone: (555) 100-1001, Membership: MEM-0001
2. Full Name: "Mary Johnson", Email: mary.johnson@outlook.com, Phone: (555) 100-1002, Membership: MEM-0002
3. Full Name: "Robert Williams", Email: robert.williams@yahoo.com, Phone: (555) 100-1003, Membership: MEM-0003
4. Full Name: "Patricia Brown", Email: patricia.brown@gmail.com, Phone: (555) 100-1004, Membership: MEM-0004
5. Full Name: "John Davis", Email: john.davis@hotmail.com, Phone: (555) 100-1005, Membership: MEM-0005
```

### Prompt 12c — Create guest customers

```
Create 3 Golf Customer records with no membership:

1. Full Name: "Michael Garcia", Email: michael.garcia@gmail.com, Phone: (555) 200-2001
2. Full Name: "Linda Martinez", Email: linda.martinez@outlook.com, Phone: (555) 200-2002
3. Full Name: "David Rodriguez", Email: david.rodriguez@yahoo.com, Phone: (555) 200-2003
```

### Prompt 12d — Verify customers

```
Show me all Golf Customer records with their name and email
```

### What to say after:

> "Eight customers — five members with varying membership statuses, three guests. This gives us a nice variety of scenarios to demo later."

---

## Scene 13 — Seed Tee Time & Booking Data (5-6 min)

### What to say:

> "Finally, let's create some tee time slots and book a few of them. We'll create morning slots for May 9th and show different booking scenarios."

### Prompt 13a — Create tee time slots

```
Create 6 Tee Time records for May 9, 2026:

1. Name: "2026-05-09 7:00 AM", Date: 2026-05-09, Time: 420, Display Time: "7:00 AM", Max Players: 4, Current Players: 0, Is Available: true
2. Name: "2026-05-09 7:10 AM", Date: 2026-05-09, Time: 430, Display Time: "7:10 AM", Max Players: 4, Current Players: 0, Is Available: true
3. Name: "2026-05-09 7:20 AM", Date: 2026-05-09, Time: 440, Display Time: "7:20 AM", Max Players: 4, Current Players: 0, Is Available: true
4. Name: "2026-05-09 7:30 AM", Date: 2026-05-09, Time: 450, Display Time: "7:30 AM", Max Players: 4, Current Players: 0, Is Available: true
5. Name: "2026-05-09 7:40 AM", Date: 2026-05-09, Time: 460, Display Time: "7:40 AM", Max Players: 4, Current Players: 0, Is Available: true
6. Name: "2026-05-09 7:50 AM", Date: 2026-05-09, Time: 470, Display Time: "7:50 AM", Max Players: 4, Current Players: 0, Is Available: true
```

### Prompt 13b — Book an active member (free)

```
Create a Tee Time Booking record:
- Booking Name: "James Smith - 2026-05-09 7:00 AM"
- Customer: James Smith
- Tee Time: 2026-05-09 7:00 AM
- Rate: Peak Rate
- Membership: MEM-0001
- Is Member: true
- Is In Good Standing: true
- Amount Charged: 0.00 (members in good standing play free)
- Status: Confirmed
- Booked On: 2026-05-07T10:00:00Z

Then update the 7:00 AM tee time to Current Players: 1
```

> "James is an active member in good standing — so he plays for free."

### Prompt 13c — Book an expired member (charged)

```
Create a Tee Time Booking record:
- Booking Name: "Patricia Brown - 2026-05-09 7:00 AM"
- Customer: Patricia Brown
- Tee Time: 2026-05-09 7:00 AM
- Rate: Peak Rate
- Membership: MEM-0004
- Is Member: true
- Is In Good Standing: false
- Amount Charged: 150.00 (expired membership, charged full rate)
- Status: Confirmed
- Booked On: 2026-05-07T11:00:00Z

Then update the 7:00 AM tee time to Current Players: 2
```

> "Patricia has a membership, but it's expired — so she's charged the full peak rate of $150."

### Prompt 13d — Book a guest (charged)

```
Create a Tee Time Booking record:
- Booking Name: "Michael Garcia - 2026-05-09 7:10 AM"
- Customer: Michael Garcia
- Tee Time: 2026-05-09 7:10 AM
- Rate: Peak Rate
- Is Member: false
- Is In Good Standing: false
- Amount Charged: 150.00
- Status: Confirmed
- Booked On: 2026-05-08T09:00:00Z

Then update the 7:10 AM tee time to Current Players: 1
```

> "Michael is a guest — no membership, full price."

### Prompt 13e — Verify bookings

```
Show me all Tee Time Booking records with the booking name, amount charged, and status
```

### What to say after:

> "Three bookings showing three different scenarios — free for an active member, full price for an expired member, and full price for a guest. The data tells a real story now."

---

## Scene 14 — Query the Data (2-3 min)

### What to say:

> "Before we wrap up Part 1, let me show you how powerful the query capabilities are. The MCP plugin lets us run SQL-style queries right from the terminal."

### Prompt 14a — Count customers

```
How many total customers do we have?
```

### Prompt 14b — Available tee times

```
Show me all available tee times for May 9, 2026 that still have open spots
```

### Prompt 14c — Revenue check

```
What's the total revenue from all confirmed bookings?
```

### What to say after:

> "Eight customers, several open tee times, and $300 in bookings. Everything checks out."

---

## Scene 15 — Part 1 Recap (1 min)

### What to say:

> "Let's recap what we just did. Starting from a completely empty environment, we:"
>
> "Created a Dataverse solution. Built five tables — Memberships, Customers, Rates, Tee Times, and Bookings. Connected them with five lookup relationships. Seeded realistic data including memberships with different statuses, member and guest customers, tee time slots, and bookings at different price points."
>
> "All of it was done through natural language using the Dataverse MCP plugin. No clicking through forms, no writing migration scripts, no manual data entry."
>
> "In Part 2, we'll build the conversational agent in Copilot Studio that puts this data to work."

---

# PART 2: Demo the Solution

---

## Scene 16 — Open Copilot Studio (2-3 min)

### What to say:

> "Now let's build the front-end experience — a conversational AI agent that customers can chat with to book tee times, check availability, and more."
>
> "I'm heading over to Copilot Studio."

### What to show:

1. Navigate to [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Select the target environment (`<yourinstance>`)
3. Click **Create** → **New agent**
4. Name it: **"Zava Golf Booking Agent"**

---

## Scene 17 — Configure Agent Instructions (3-4 min)

### What to say:

> "Every agent needs instructions — this is the system prompt that tells it who it is, what it can do, and how it should behave."

### Instructions to paste into Copilot Studio:

```
You are a golf course booking assistant for Zava Golf Course.

You help customers with the following tasks:
- Book tee times
- Check tee time availability
- Look up membership status
- Answer questions about rates and pricing

Business rules:
- Members with Active membership status and in good standing play for FREE
- Members with Expired or Suspended memberships are charged the standard rate
- Guest (non-member) customers are always charged the standard rate
- Peak Rate: $150 (7:00 AM – 12:00 PM)
- Off-Peak Rate: $100 (12:00 PM – 5:00 PM)
- Tee times are available every 10 minutes from 7:00 AM to 5:00 PM
- Maximum 4 players per tee time slot

When booking a tee time:
1. Ask for the customer's name
2. Look up the customer to check membership status
3. Check availability for the requested date and time
4. Confirm the booking and inform them of any charges

Always be friendly, professional, and knowledgeable about golf. If you can't help with something, offer to connect them with the pro shop staff at (555) GOLF-123.
```

### What to say after:

> "These instructions give the agent all the business context it needs — pricing rules, membership logic, the booking workflow. The generative AI will use these to handle conversations naturally."

---

## Scene 18 — Connect Dataverse Tables (3-5 min)

### What to say:

> "Now we need to give the agent access to our data. We'll enable generative actions so the agent can query and create records in our Dataverse tables."

### What to show:

1. Go to **Actions** or **Knowledge** in Copilot Studio
2. Enable Dataverse connector / generative actions
3. Select and enable access to:
   - Golf Customer
   - Golf Membership
   - Golf Rate
   - Tee Time
   - Tee Time Booking
4. Configure the Conversation Start topic with a welcome message:

```
Welcome to Zava Golf Course! ⛳ I'm your booking assistant. I can help you book tee times, check availability, look up membership status, or answer questions about rates. How can I help?
```

5. Publish the agent

### What to say after:

> "Our agent is published and has access to all five tables. Let's take it for a spin."

---

## Scene 19 — Demo: Check Availability (2-3 min)

### What to say:

> "Let's start with a simple question — what tee times are available?"

### Demo conversation:

**You type:**
```
What tee times do you have available for May 9th?
```

**Expected agent response:** Lists available tee time slots for May 9, 2026 showing which ones have open spots.

### What to say after:

> "The agent queried our Tee Time table, filtered for May 9th, and found the available slots. Notice it shows the human-friendly display times, not raw minute values."

---

## Scene 20 — Demo: Member Booking — Free (3-4 min)

### What to say:

> "Now let's book a tee time as a member in good standing. This should be free."

### Demo conversation:

**You type:**
```
I'd like to book a tee time. My name is Mary Johnson.
```

**Expected agent behavior:**
- Looks up Mary Johnson in Golf Customer table
- Finds her linked membership (MEM-0002, Active)
- Confirms she's in good standing

**You type:**
```
I'd like the 7:20 AM slot please.
```

**Expected agent response:** Confirms the booking, notes that as an active member she plays for free, creates the booking record.

### What to say after:

> "The agent looked up Mary, confirmed her active membership, and booked her in for free. All that membership logic we put in the instructions — the agent applied it automatically."

---

## Scene 21 — Demo: Guest Booking — Charged (3-4 min)

### What to say:

> "Now let's see what happens when a guest — someone without a membership — tries to book."

### Demo conversation:

**You type:**
```
Hi, I'd like to book a tee time for tomorrow morning. My name is David Rodriguez.
```

**Expected agent behavior:**
- Looks up David Rodriguez
- Finds no membership link
- Proceeds with standard pricing

**You type:**
```
The 7:30 AM slot for 2 players please.
```

**Expected agent response:** Confirms pricing ($150 peak rate), creates the booking.

### What to say after:

> "David's a guest, so he's charged the full peak rate. The agent handled the pricing logic correctly without any custom code."

---

## Scene 22 — Demo: Membership Status Check (2-3 min)

### What to say:

> "Let's try a membership inquiry — someone wants to check if their membership is still valid."

### Demo conversation:

**You type:**
```
Can you check my membership status? My name is Patricia Brown.
```

**Expected agent response:** Looks up Patricia Brown, finds membership MEM-0004 with Expired status, informs her that her membership has expired and suggests renewal or contacting the pro shop.

### What to say after:

> "The agent found Patricia's expired membership and handled it gracefully — informing her of the status and offering next steps."

---

## Scene 23 — Demo: Rate Inquiry (1-2 min)

### What to say:

> "One more scenario — a simple pricing question."

### Demo conversation:

**You type:**
```
How much does it cost to play a round of golf?
```

**Expected agent response:** Explains the two rate tiers — Peak Rate ($150, 7 AM – 12 PM) and Off-Peak Rate ($100, 12 PM – 5 PM). May also mention that members in good standing play for free.

### What to say after:

> "Clean, accurate pricing information pulled straight from our Rate table."

---

## Scene 24 — Wrap-Up & Recap (2 min)

### What to say:

> "And that's it! Let's recap what we built today."
>
> "In Part 1, we used the Dataverse MCP plugin to build our entire data model through natural language — five tables, five relationships, and realistic sample data. No forms, no code, no manual configuration."
>
> "In Part 2, we created a conversational AI agent in Copilot Studio that can:"
>
> - "Check tee time availability"
> - "Book tee times with proper pricing"
> - "Handle membership lookups and apply member benefits"
> - "Answer pricing questions"
>
> "The combination of Dataverse MCP for backend development and Copilot Studio for the conversational front-end is incredibly powerful. You get a production-ready data layer and an AI agent that understands your business rules — all built in about 30 minutes."
>
> "Thanks for watching. If you have questions, drop them in the comments."

---

# Pre-Recording Checklist

- [ ] Clean Dataverse environment at `https://<yourinstance>.crm.dynamics.com/` (no existing custom tables)
- [ ] MCP plugin configured and connected to the environment
- [ ] Terminal / VS Code zoomed to at least 150% for screen readability
- [ ] Screen recording software running (OBS, Camtasia, etc.)
- [ ] Copilot Studio access confirmed in the target environment
- [ ] Do a dry run of at least Scenes 2-4 to confirm MCP connectivity and table creation works
- [ ] Have this script open on a second monitor or printed out
- [ ] Close unnecessary tabs/apps to reduce distractions on screen

---

# Tips for Recording

- **Pause briefly** after each prompt so viewers can read what you typed
- **Narrate while waiting** — explain the business logic while the MCP tool executes
- **If something fails**, don't panic — show the error and how you fix it (real-world authenticity)
- **Keep energy up** during the data seeding section — it's repetitive, so your narration carries it
- **For Part 2**, slow down during the demo conversations — let the agent responses render fully before reacting
