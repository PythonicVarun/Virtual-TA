#!/usr/bin/env python3
"""
get_discourse_threads.py

Download all Discourse threads in a specific category between two dates
and include all posts from each thread via pagination.

Usage:
    python get_discourse_threads.py \
      --base-url      "https://discourse.onlinedegree.iitm.ac.in" \
      --category-path "courses/tds-kb/34" \
      --start-date    "2025-05-01" \
      --end-date      "2025-05-10" \
      --output-dir    "data/raw_discourse_threads" \
      [--api-key KEY --api-username USER] \
      [--cookies "name=value; name2=value2"]
"""

import os
import json
import argparse
import requests
from math import ceil
from datetime import datetime, timezone
from dateutil import parser as dateparser


def parse_args():
    p = argparse.ArgumentParser(
        description="Download Discourse threads from a specific category between two dates"
    )

    p.add_argument(
        "--base-url",
        required=True,
        help="Base URL of your Discourse site, e.g. https://discourse.example.com",
    )
    p.add_argument(
        "--category-path", required=True, help="Category path, e.g. courses/tds-kb/34"
    )
    p.add_argument(
        "--start-date",
        required=True,
        help="Earliest creation date (inclusive), YYYY-MM-DD",
    )
    p.add_argument(
        "--end-date", required=True, help="Latest creation date (inclusive), YYYY-MM-DD"
    )
    p.add_argument(
        "--output-dir", required=True, help="Directory to save thread JSON files"
    )

    auth = p.add_argument_group("authentication (at least one)")
    auth.add_argument(
        "--api-key", metavar="KEY", help="Discourse API key (requires --api-username)"
    )
    auth.add_argument(
        "--api-username",
        metavar="USER",
        help="Discourse API username (requires --api-key)",
    )
    auth.add_argument(
        "--cookies",
        metavar="COOKIE_HEADER",
        help="Raw Cookie header to authenticate (e.g. 'name=val; name2=val2')",
    )

    return p.parse_args()


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def fetch_json(url, params=None, headers=None):
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()


def main():
    args = parse_args()

    if not (args.cookies or (args.api_key and args.api_username)):
        raise SystemExit(
            "Error: you must supply either:\n"
            "  • --cookies COOKIE_HEADER\n"
            "or\n"
            "  • both --api-key KEY and --api-username USER"
        )

    # Parse dates as UTC datetimes
    start_dt = datetime.fromisoformat(args.start_date).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(args.end_date).replace(tzinfo=timezone.utc)
    end_dt = end_dt.replace(hour=23, minute=59, second=59)

    ensure_dir(args.output_dir)

    # Base headers
    headers = {
        "User-Agent": "Virtual TA - Discourse API Client",
        "X-Report-Abuse": "hello@pythonicvarun.me",
    }

    # Attach whichever auth method
    if args.api_key:
        headers["Api-Key"] = args.api_key
        headers["Api-Username"] = args.api_username
    else:
        headers["Cookie"] = args.cookies

    page = 0
    downloaded = 0

    print(
        f"→ Scanning /c/{args.category_path}.json pages for threads from {start_dt.date()} to {end_dt.date()}…"
    )

    while True:
        resp = fetch_json(
            f"{args.base_url}/c/{args.category_path}.json",
            params={"page": page, "per_page": 100},
            headers=headers,
        )

        topics = resp.get("topic_list", {}).get("topics", [])
        if not topics:
            print("→ No more topics returned; done.")
            break

        for topic in topics:
            created = topic.get("created_at")
            if not created:
                continue

            created_dt = dateparser.isoparse(created)
            # skip anything before our start date
            if created_dt < start_dt:
                continue

            # within window?
            if start_dt <= created_dt <= end_dt:
                tid = topic["id"]
                title = topic.get("title", "")
                out_f = os.path.join(args.output_dir, f"thread_{tid}.json")

                if os.path.exists(out_f):
                    print(f"  [skip] {tid} already exists")
                    continue

                first = fetch_json(
                    f"{args.base_url}/t/{tid}.json",
                    params={"track_visit": False, "forceLoad": True, "page": 1},
                    headers=headers,
                )

                posts = first.get("post_stream", {}).get("posts", [])
                total_posts = first.get("posts_count") or len(
                    first.get("post_stream", {}).get("stream", [])
                )
                per_page = len(posts)

                if per_page and total_posts > per_page:
                    pages = ceil(total_posts / per_page)
                    for pnum in range(2, pages + 1):
                        more = fetch_json(
                            f"{args.base_url}/t/{tid}.json",
                            params={
                                "track_visit": False,
                                "forceLoad": True,
                                "page": pnum,
                            },
                            headers=headers,
                        )
                        more_posts = more.get("post_stream", {}).get("posts", [])
                        if not more_posts:
                            break
                        posts.extend(more_posts)

                # Save combined data
                combined = first
                combined["post_stream"]["posts"] = posts

                with open(out_f, "w", encoding="utf-8") as fd:
                    json.dump(combined, fd, ensure_ascii=False)

                print(
                    f"  [save]  {tid} - {title} ({created_dt.date()}) [posts: {len(posts)}]"
                )
                downloaded += 1

        page += 1

    print(f"✔ Completed: {downloaded} threads saved to “{args.output_dir}”.")


if __name__ == "__main__":
    main()
