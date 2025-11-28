# Degen Index – Public Reddit API Demo

This repository contains a **minimal public demonstration** of how the Degen Index
project will access the Reddit API for *read-only analysis* of public discussion
threads. This repo exists to provide transparency for Reddit's API review team and
to give an example of the ingestion pattern used in the production system.

The production version of Degen Index includes:
- daily sentiment aggregation for r/wallstreetbets “What Are Your Moves Tomorrow”
- stock/ticker trend tracking over time
- meme heat analysis
- charts and summaries that point users **back to Reddit threads**
- *no* redistribution of Reddit content or datasets
- *no* ML training on Reddit data
- *no* analysis of individual Redditors or private data

This public repository only contains:
- a simple example script demonstrating API access (`ingest_demo.py`)
- documentation of intended behavior
- safety and compliance notes

The **full pipeline**, analytics engine, UI, and storage layer live in a private repo
and will be partially open-sourced later once the initial launch is complete.

---

## 🔍 Project Purpose

Degen Index analyzes high-volume public WSB threads and produces:
- aggregated ticker sentiment
- daily trend summaries
- a historical “degen index”
- highlight comments (with attribution + links back to Reddit)
- narrative summaries for easier navigation of massive threads

All output is **transformative analytics** — the project does **not** sell or
redistribute Reddit comments.

The goal is to make large Reddit discussions easier for Redditors to
understand, explore, and navigate.

---

## 📘 Example: Fetching a Thread via Reddit API

The included script (`ingest_demo.py`) shows a minimal read-only API call using
`praw` to fetch a small number of comments from a public thread.

This demonstrates the access pattern the production system will use, without
exposing private logic or pipeline components.

---

## 🚫 What This Project Does NOT Do

To comply with Reddit’s terms, Degen Index does **not**:

- sell Reddit comments, data, or datasets  
- redistribute comments in bulk  
- store private messages or do private APIs  
- analyze individual Reddit users  
- attempt to reconstruct or deanonymize user identity  
- train machine learning models on Reddit data  

All inference is **read-only** and used only for generating analytics summaries.

---

## 🔗 Platform Link

The final dashboard and analytics UI will be hosted at:

**https://degenindex.com**  
(placeholder until launch)

---

## 🔧 Requirements

- Python 3.10+
- Reddit API credentials ([create an app here](https://www.reddit.com/prefs/apps))
- `praw` library for Reddit API access

---

## 🚀 Installation

```bash
pip install praw
```

---

## 📊 Usage

```bash
# Set your Reddit API credentials
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"

# Run the demo with a WSB thread submission ID
python ingest_demo.py --submission-id 1k0abc123
```

To find a submission ID, look at a Reddit URL like:
`https://reddit.com/r/wallstreetbets/comments/1k0abc123/what_are_your_moves_tomorrow/`

The submission ID is the alphanumeric string after `/comments/` (in this case: `1k0abc123`).

---

## 📈 Pipeline Overview

The demo script illustrates the analysis pipeline used by Degen Index:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   1. INGESTION  │ ──▶ │ 2. CLASSIFICA-  │ ──▶ │   3. OUTPUT     │
│                 │     │      TION       │     │                 │
│ Fetch comments  │     │ Analyze each    │     │ Structured      │
│ from Reddit     │     │ comment for     │     │ JSON per        │
│ via PRAW        │     │ sentiment,      │     │ comment         │
│                 │     │ tickers, mood   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Stage 1: Ingestion**
- Fetches public comments from a Reddit thread
- Uses PRAW (Python Reddit API Wrapper)
- Read-only access, no data storage

**Stage 2: Classification** (mocked in this demo)
- Analyzes each comment for:
  - **Sentiment**: bullish / bearish / neutral / mixed
  - **Tickers**: Stock symbols mentioned (e.g., NVDA, SPY, TSLA)
  - **Mood**: euphoria, fear, cope, confusion, etc.
  - **Degen score**: Risk level 0-10 (0 = conservative, 10 = YOLO)
  - **Meme score**: Humor level 0-10 (0 = serious, 10 = pure shitpost)

In production, classification is performed by an LLM. This demo uses mock
outputs to illustrate the schema without exposing production logic.

---

## 📝 Example Output

When you run the demo, you'll see output like:

```
=== DEGEN INDEX DEMO ===
Thread: What Are Your Moves Tomorrow, November 27, 2025

--- Comment 1 ---
Author: u/example_user
Upvotes: 42
Text: "NVDA calls printing tomorrow, earnings gonna be insane..."

Classification:
{
  "is_trade_plan": true,
  "is_meme": false,
  "tickers": ["NVDA"],
  "sentiment": {
    "trade_direction": "bullish",
    "sentiment_confidence": 8,
    "is_sarcastic": false
  },
  "primary_mood": "euphoria",
  "degen_score": 7,
  "meme_score": 2
}
```

This structured output enables aggregation across hundreds of comments to
produce daily sentiment summaries, ticker trend tracking, and the "Degen Index."

---

## 🔒 Privacy & Compliance

This demo and the production system:
- Only access **public** Reddit threads
- Perform **read-only** operations
- Do **not** store raw comments or user data
- Link back to original Reddit content with attribution
- Produce **transformative analytics**, not content redistribution

See the compliance section above for full details.
