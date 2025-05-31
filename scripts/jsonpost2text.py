#!/usr/bin/env python3
"""
Convert Discourse thread JSON files to plain-text Markdown summaries.
Supports processing a single file or all JSON files in a directory.
Usage:
    jsonpost2text.py input_path [--output OUTPUT_DIR]

Examples:
    jsonpost2text.py thread.json
    jsonpost2text.py /path/to/json_dir --output ./out_texts
"""
import sys
import json
from pathlib import Path
import argparse
from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    """Strip HTML tags and collapse whitespace to plain text."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned = []
    prev_blank = False
    for ln in lines:
        if not ln:
            if not prev_blank:
                cleaned.append("")
            prev_blank = True
        else:
            cleaned.append(ln)
            prev_blank = False
    return "\n".join(cleaned).strip()


po = set()


def thread_to_text(data: dict) -> str:
    """Convert JSON thread data to a formatted text block."""
    posts = data.get("post_stream", {}).get("posts", [])
    posts.sort(key=lambda p: p.get("created_at", ""))
    out_lines = []
    for post in posts:
        ts = post.get("created_at", "")
        name = post.get("name") or post.get("username")
        user = post.get("username", "")
        user_post = post.get("user_title", None)
        if user_post not in po:
            po.add(user_post)

        header = f"[{ts}] {name} (@{user}{(': ' + user_post) if user_post else ''})"
        body = html_to_text(post.get("cooked", ""))
        out_lines.append(header)
        out_lines.append(body)
        out_lines.append("")
    return "\n".join(out_lines).strip()


def process_file(input_file: Path, output_dir: Path) -> None:
    """Read a JSON file and write the corresponding text file."""
    try:
        with input_file.open(encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}", file=sys.stderr)
        return

    post_id = data.get("id", input_file.stem)
    title = data.get("title", "")
    created_at = data.get("created_at", "")
    text_content = thread_to_text(data)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"thread_{post_id}.txt"
    try:
        with out_path.open("w", encoding="utf-8") as txt:
            txt.write("---\n")
            txt.write(f"id:          {post_id}\n")
            txt.write(f"title:       {title}\n")
            txt.write(f"created_at:  {created_at}\n")
            txt.write("---\n\n")
            txt.write(text_content)
        print(f"Processed {input_file} -> {out_path}")
    except Exception as e:
        print(f"Error writing {out_path}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Process Discourse thread JSON files to text summaries."
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to a JSON file or a directory of JSON files.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("./discourse_posts"),
        help="Output directory for text files.",
    )
    args = parser.parse_args()

    if not args.input_path.exists():
        print(f"Error: {args.input_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.input_path.is_file():
        process_file(args.input_path, args.output)
    else:
        # Directory: process all .json files
        json_files = sorted(args.input_path.glob("*.json"))
        if not json_files:
            print(f"No JSON files found in {args.input_path}.", file=sys.stderr)
            sys.exit(1)

        for jf in json_files:
            process_file(jf, args.output)


if __name__ == "__main__":
    main()
    print(po)
