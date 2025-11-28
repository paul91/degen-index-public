#!/usr/bin/env python3
"""
Degen Index - Reddit API Demo

This script demonstrates how Degen Index accesses the Reddit API and the type
of analysis performed on comments. It is intended for Reddit API review.

Pipeline stages:
1. INGESTION - Fetch comments from a public Reddit thread via PRAW
2. CLASSIFICATION - Analyze sentiment, tickers, mood (mocked in this demo)

This is NOT production code. Real classification uses an LLM to analyze each
comment and return structured JSON. This demo uses mock outputs to illustrate
the schema without exposing production logic.

Usage:
    export REDDIT_CLIENT_ID="your_client_id"
    export REDDIT_CLIENT_SECRET="your_client_secret"
    python ingest_demo.py --submission-id <reddit_post_id>
"""

import argparse
import json
import os
import random

import praw


# Common WSB tickers for mock classification
COMMON_TICKERS = ["SPY", "QQQ", "NVDA", "TSLA", "AAPL", "AMD", "AMZN", "META", "GOOGL", "MSFT"]
MOODS = ["euphoria", "fear", "despair", "cope", "smug", "confusion", "neutral"]
DIRECTIONS = ["bullish", "bearish", "mixed", "neutral"]


def mock_classify_comment(body: str) -> dict:
    """
    Demonstrates the classification schema used in production.

    In production, an LLM analyzes each comment and returns structured JSON
    matching this schema. This mock version uses simple heuristics to show
    the output format.

    Classification fields:
    - is_trade_plan: True if discussing a specific trade/position
    - is_meme: True if primarily humorous/satirical
    - is_commentary: True if making a market observation or prediction
    - tickers: Stock symbols explicitly mentioned in the text
    - primary_mood: Dominant emotional tone of the comment
    - sentiment: Trade direction, confidence level, sarcasm detection
    - degen_score: Risk level 0-10 (0=conservative, 10=YOLO options)
    - meme_score: Humor level 0-10 (0=serious analysis, 10=pure shitpost)
    """
    body_upper = body.upper()

    # Simple ticker extraction (real version is more sophisticated)
    found_tickers = [t for t in COMMON_TICKERS if t in body_upper]

    # Simple sentiment heuristics (real version uses LLM)
    bullish_words = ["moon", "calls", "buy", "long", "rocket", "tendies", "print"]
    bearish_words = ["puts", "short", "drill", "crash", "dump", "rug"]

    bullish_count = sum(1 for w in bullish_words if w in body.lower())
    bearish_count = sum(1 for w in bearish_words if w in body.lower())

    if bullish_count > bearish_count:
        direction = "bullish"
    elif bearish_count > bullish_count:
        direction = "bearish"
    else:
        direction = "neutral"

    # Detect trade plans vs commentary
    trade_indicators = ["bought", "buying", "sold", "selling", "holding", "position", "calls", "puts"]
    is_trade = any(w in body.lower() for w in trade_indicators)

    # Detect memes/humor
    meme_indicators = ["lmao", "lol", "ape", "smooth brain", "wife's boyfriend", "wendy's"]
    meme_count = sum(1 for w in meme_indicators if w in body.lower())

    return {
        "is_trade_plan": is_trade,
        "is_meme": meme_count >= 2,
        "is_commentary": not is_trade or len(found_tickers) > 0,
        "tickers": found_tickers,
        "primary_mood": random.choice(MOODS) if meme_count == 0 else "euphoria",
        "topic_type": "single_stock" if len(found_tickers) == 1 else "index_macro" if found_tickers else "other",
        "sentiment": {
            "trade_direction": direction,
            "sentiment_confidence": min(10, max(1, bullish_count + bearish_count + 3)),
            "is_sarcastic": "/s" in body or meme_count >= 2,
        },
        "degen_score": min(10, 3 + meme_count + (2 if is_trade else 0)),
        "meme_score": min(10, meme_count * 3),
    }


def print_classification(index: int, comment, classification: dict) -> None:
    """Pretty-print a comment and its classification."""
    print(f"\n{'='*60}")
    print(f"Comment #{index}")
    print(f"{'='*60}")
    print(f"Author: u/{comment.author.name if comment.author else '[deleted]'}")
    print(f"Upvotes: {comment.score}")
    print(f"Permalink: https://reddit.com{comment.permalink}")
    print(f"\nText (truncated):")
    print(f'  "{comment.body[:300]}{"..." if len(comment.body) > 300 else ""}"')
    print(f"\nClassification:")
    print(json.dumps(classification, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Degen Index Reddit API Demo - Fetch and classify WSB comments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python ingest_demo.py --submission-id 1k0abc123
    python ingest_demo.py --submission-id 1k0abc123 --limit 10

Environment variables:
    REDDIT_CLIENT_ID      Your Reddit app client ID
    REDDIT_CLIENT_SECRET  Your Reddit app client secret
    REDDIT_USER_AGENT     Optional custom user agent (default: DegenIndexDemo/0.1)
        """,
    )
    parser.add_argument(
        "--submission-id",
        required=True,
        help="Reddit submission ID (the alphanumeric string from the URL)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of top-level comments to fetch (default: 5)",
    )

    args = parser.parse_args()

    # Validate environment
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: Missing Reddit API credentials.")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.")
        print("\nTo get credentials, create an app at: https://www.reddit.com/prefs/apps")
        return 1

    # =========================================================================
    # STAGE 1: INGESTION
    # Fetch comments from Reddit via PRAW (read-only access)
    # =========================================================================
    print("\n" + "=" * 60)
    print("STAGE 1: INGESTION")
    print("Fetching comments from Reddit...")
    print("=" * 60)

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=os.getenv("REDDIT_USER_AGENT", "DegenIndexDemo/0.1"),
    )

    try:
        submission = reddit.submission(id=args.submission_id)
        # Force fetch to validate the submission exists
        _ = submission.title
    except Exception as e:
        print(f"ERROR: Could not fetch submission '{args.submission_id}'")
        print(f"Details: {e}")
        return 1

    print(f"\nThread: {submission.title}")
    print(f"URL: https://reddit.com{submission.permalink}")
    print(f"Subreddit: r/{submission.subreddit.display_name}")
    print(f"Upvotes: {submission.score}")

    # Fetch top-level comments only (no "load more" expansion for demo)
    submission.comments.replace_more(limit=0)
    comments = list(submission.comments)[:args.limit]

    print(f"\nFetched {len(comments)} top-level comments")

    # =========================================================================
    # STAGE 2: CLASSIFICATION
    # Analyze each comment (mocked - real version uses LLM)
    # =========================================================================
    print("\n" + "=" * 60)
    print("STAGE 2: CLASSIFICATION (mocked)")
    print("Analyzing sentiment, tickers, and mood...")
    print("=" * 60)

    classifications = []
    for i, comment in enumerate(comments, 1):
        classification = mock_classify_comment(comment.body)
        classifications.append(classification)
        print_classification(i, comment, classification)

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_tickers = []
    for c in classifications:
        all_tickers.extend(c["tickers"])

    bullish = sum(1 for c in classifications if c["sentiment"]["trade_direction"] == "bullish")
    bearish = sum(1 for c in classifications if c["sentiment"]["trade_direction"] == "bearish")
    neutral = len(classifications) - bullish - bearish

    print(f"\nComments analyzed: {len(classifications)}")
    print(f"Unique tickers mentioned: {list(set(all_tickers)) or 'None'}")
    print(f"Sentiment breakdown: {bullish} bullish, {bearish} bearish, {neutral} neutral")
    print(f"Average degen score: {sum(c['degen_score'] for c in classifications) / len(classifications):.1f}/10")

    print("\n" + "-" * 60)
    print("NOTE: This demo uses mock classification. In production,")
    print("an LLM analyzes each comment for more accurate results.")
    print("-" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
