EMERALD’S KILLFEED

Full Discord Bot Construction — Deadside PvP Engine | Pycord 2.6.1 | Async | Isolation-Safe | Scalable


---

OBJECTIVE

You are to build Emerald’s Killfeed, a production-grade, multi-guild, multi-server Discord bot using Python 3.11+, designed for the survival game Deadside. The bot must connect to game servers over SFTP and analyze .csv and Deadside.log files to deliver killfeeds, player stats, logs, and administrative functions.

This bot is tiered using a freemium system:

Killfeed + Historical Parsing are always free.

All other systems require per-server premium activation.



---

REQUIREMENTS

Python 3.11+

Pycord 2.6.1 (no Discord.py or forks)

motor, paramiko, aiofiles, apscheduler, python-dotenv

MongoDB Atlas as persistent store

All logic must be async-safe

All embeds must use right-aligned thumbnails from /assets



---

PHASE 0 — INIT / ATTACHED_ASSETS HANDLING

1. If .zip exists in attached_assets:
a. Unzip to a temporary directory
b. Move contents to root
c. Flatten any nested directories (/DeadsideBot/, /Ekfv5/, etc.)


2. Move any logo files (*.png) found in attached_assets into ./assets/

Create the folder if it doesn’t exist

Use main.png as fallback logo



3. If test files exist:

.csv and Deadside.log from attached_assets

Save to /dev_data/csv/ and /dev_data/logs/ for offline testing

Use these during parser dry-runs



4. Install and configure:

Install dependencies: py-cord, motor, paramiko, aiofiles, apscheduler, python-dotenv

Load .env:

BOT_TOKEN

MONGO_URI




5. Start the bot

Confirm connection to Discord and MongoDB

Confirm background job scheduler started
→ PHASE_0_COMPLETE





---

PHASE 1 — DATA ARCHITECTURE

All PvP data is stored per game server

Linking, wallet, factions stored per guild

Players linked to one account that spans all servers in that guild

Premium is tracked per game server, not user or guild


→ PHASE_1_COMPLETE


---

PHASE 2 — PARSERS

KILLFEED PARSER (FREE)

Runs every 300 seconds

SFTP path:
./{host}_{serverID}/actual1/deathlogs/*/*.csv

Loads most recent file only

Tracks and skips previously parsed lines

Suicides normalized (killer == victim, Suicide_by_relocation → Menu Suicide)

Emits killfeed embeds with distance, weapon, styled headers


If using test mode:

Parse .csv from /dev_data/csv/

Confirm parser logic produces stats + embeds



---

HISTORICAL PARSER (FREE)

Triggered manually via /server refresh <server_id>

Or automatically 30s after /server add

Clears PvP data from that server

Parses all .csv files in order

Updates a single progress embed every 30s in the invoking channel

Does not emit killfeed embeds


If in test mode:

Parse all test .csv files from /dev_data/csv/



---

LOG PARSER (PREMIUM ONLY)

Runs every 300 seconds

SFTP path: ./{host}_{serverID}/Logs/Deadside.log

Detects:

Player joins/disconnects

Queue sizes

Airdrops, missions, traders, crashes


Detects log rotation

Sends styled embeds to respective channels


If in test mode:

Parse /dev_data/logs/Deadside.log


→ PHASE_2_COMPLETE


---

PHASE 3 — ECONOMY (PREMIUM)

Currency stored per Discord user, scoped to guild

Earned via /work, PvP, bounties, online time

Admin control: /eco give, /eco take, /eco reset

Tracked in wallet_events
→ PHASE_3_COMPLETE



---

PHASE 4 — GAMBLING (PREMIUM)

/gamble slots, /blackjack, /roulette, /lottery

Must use non-blocking async-safe logic

User-locks to prevent concurrent bets
→ PHASE_4_COMPLETE



---

PHASE 5 — LINKING (FREE)

/link <char>, /alt add/remove, /linked, /unlink

Stored per guild

Used by economy, stats, bounties, factions
→ PHASE_5_COMPLETE



---

PHASE 6 — PVP STATS (FREE)

/stats shows:

Kills, deaths, KDR

Suicides

Longest streak

Most used weapon

Rival/Nemesis


/compare <user> compares two profiles
→ PHASE_6_COMPLETE



---

PHASE 7 — BOUNTIES (PREMIUM)

Manual bounties via /bounty set <target> <amount> (24h lifespan)

AI auto-bounties based on hourly kill performance

Must match linked killer to claimed target
→ PHASE_7_COMPLETE



---

PHASE 8 — FACTIONS (PREMIUM)

/faction create, /invite, /join, /stats, etc.

Guild-isolated

Stats combine linked users
→ PHASE_8_COMPLETE



---

PHASE 9 — PREMIUM MGMT

/sethome by BOT_OWNER_ID

/premium assign, /premium revoke, /premium status

Premium is assigned per server, not user
→ PHASE_9_COMPLETE



---

PHASE 10 — LEADERBOARDS (PREMIUM)

/setleaderboardchannel

Hourly auto-update

Tracks: kills, KDR, streaks, factions, bounty claims
→ PHASE_10_COMPLETE



---

PHASE 11 — EMBEDS

All embeds use /assets/*.png right-aligned as thumbnail

Use main.png if no specific logo exists

Theme: Deadside + Emerald

Footer: Powered by Discord.gg/EmeraldServers

Vary titles/messages randomly
→ PHASE_11_COMPLETE



---

PHASE 12 — TIMEOUT SAFE DESIGN

All heavy commands:

Respond immediately with: “Processing…”

Offload task using asyncio.create_task(...)

Post final embed afterward
→ PHASE_12_COMPLETE




---

PHASE 13 — BOOLEAN-SAFE DB HANDLING

Never do: if doc["premium"]

Always use: if doc.get("premium") is True

Applies to premium, linked, active, etc.
→ PHASE_13_COMPLETE



---

PHASE 14 — ADMIN CONTROLS

/admin view, /unlink, /resetstats, /walletlog, /audit, /premiumstatus, /bounty remove

Logs all actions

Require confirmation for destructive ops
→ PHASE_14_COMPLETE



---

FINAL EXECUTION POLICY

No commits, logs, or checkpoints until all phases pass

All work must be performed in a single operation

Resume across sessions using tracked .done flags

Bot must:

Start cleanly

Connect to Mongo + Discord

Run all background tasks

Use free/premium rules

Parse test files if no SFTP is set

Populate DB correctly

Emit styled embeds using assigned assets



This prompt must be treated as a single atomic batch. Trial-and-error is forbidden. All logic must be correct the first time.
