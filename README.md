# Facility CDE — WhatsApp API v2

Industrial facility assistant. Workers query machine data via WhatsApp.
Powered by Nemotron Nano 3 (NVIDIA) + Google Embeddings + ChromaDB.

---

## What changed in v2

- **LLM**: Switched from Gemini to Nemotron Nano 3 via NVIDIA API (OpenAI-compatible)
- **Central LLM client**: `core/llm.py` — one place to swap models
- **SQLite WAL mode**: 10x faster reads, safe concurrent access
- **Batch DB writes**: `executemany()` — handles 100s of findings in one transaction
- **Severity column**: auto-computed from confidence on every finding
- **Ingest log table**: full audit trail of every file processed
- **Better intent prompt**: Hindi/Hinglish examples, filters extraction
- **Better formatters**: findings grouped by severity, tree-style summary
- **New commands**: `search`, `linestatus`
- **Permanent webhook URL**: deploy to Railway, set once in Twilio, never change again
- **Message chunking**: long replies auto-split (WhatsApp 1600 char limit)
- **`/status` endpoint**: live count of assets, findings, users

---

## Setup

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
```

Fill `.env`:
```
NEMOTRON_API_KEY=     ← from build.nvidia.com (free tier available)
NEMOTRON_BASE_URL=https://integrate.api.nvidia.com/v1
NEMOTRON_MODEL=nvidia/llama-3.1-nemotron-nano-8b-instruct
GOOGLE_API_KEY=       ← for embeddings only (free)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
ADMIN_PHONE=whatsapp:+91XXXXXXXXXX
VERIFY_TOKEN=any_secret_string
```

### 3. Seed database
```bash
PYTHONPATH=. python seed_data.py
```

### 4. Test locally
```bash
PYTHONPATH=. python terminal_chat.py
```

Try: `summary M14`, `findings BATCH1`, `critical`, `list`

---

## Deploy to Railway (permanent webhook URL)

This is how you get a fixed URL so you never touch Twilio settings again.

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "facility cde v2"
git remote add origin https://github.com/yourname/facility-cde.git
git push -u origin main
```

### Step 2 — Create Railway project
1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select your repo
3. Railway auto-detects `Procfile` and builds

### Step 3 — Add environment variables in Railway
In Railway dashboard → your project → Variables, add every value from your `.env`

Also add:
```
DB_PATH=/tmp/facility.db
```

### Step 4 — Get your permanent URL
Railway dashboard → Settings → Domains → Generate Domain

You get something like:
```
https://facility-cde-production.up.railway.app
```

This URL **never changes**. Set it once in Twilio and forget it.

### Step 5 — Set Twilio webhook (once, permanently)
1. [console.twilio.com](https://console.twilio.com) → Messaging → Try it out → WhatsApp sandbox settings
2. "When a message comes in":
```
https://facility-cde-production.up.railway.app/webhook/webhook
```
Method: `HTTP POST` → Save

That's it. Never change this again even if you redeploy.

### Step 6 — Verify deployment
```
https://facility-cde-production.up.railway.app/
→ {"status":"ok","service":"Facility CDE WhatsApp API","version":"2.0"}

https://facility-cde-production.up.railway.app/status
→ {"assets":6,"findings":13,"users":1,"ingest_log":[...]}
```

### Step 7 — Text your bot
From WhatsApp, message +14155238886:
```
help
summary M14
findings BATCH1
critical
```

---

## Railway SQLite note

Railway's filesystem resets on redeploy. Your DB is wiped each time.

**For persistent data, add Railway Volume:**
Railway dashboard → your project → + New → Volume → mount at `/data`

Then set:
```
DB_PATH=/data/facility.db
```

Or migrate to PostgreSQL — only `core/db.py` changes, nothing else.

---

## Adding a new data format

1. Add signature to `ingestion/detector.py` → `SCHEMA_SIGNATURES`
2. Add normaliser to `ingestion/normalisers.py`
3. Add to `JSON_HANDLERS` or `EXCEL_HANDLERS` in `ingestion/universal.py`

---

## Supported commands

```
machine [id or name]            asset info and location
findings [id or name]           defects grouped by severity
notes [id or name]              expert notes
summary [id or name]            full overview with severity counts
list                            all assets
critical                        high confidence / critical findings
latest                          5 most recent inspections
search [keyword]                full-text search across findings
linestatus [line name]          production line overview
ask [question]                  RAG search across documents
image [id]                      CV output image
addnote [id] [text]             add expert note
report [id] [description]       field report
adduser [phone] [name] [role]   register worker
removeuser [phone]              deactivate worker
listusers                       list all workers
help                            your available commands
```

---

## NVIDIA Nemotron API (free tier)

1. Go to [build.nvidia.com](https://build.nvidia.com)
2. Sign up free
3. Go to API → Generate Key
4. Free tier: 1000 credits/month — enough for 50 workers at MVP scale
5. Model: `nvidia/llama-3.1-nemotron-nano-8b-instruct`
