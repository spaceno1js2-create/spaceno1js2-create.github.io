#!/usr/bin/env python3
import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path.home() / "blog" / "quartz"
CONTENT_DIR = ROOT / "content" / "posts"


def run(cmd, check=True):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s가-힣-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = text.strip("-")
    return text[:60] or "post"


def main():
    parser = argparse.ArgumentParser(description="Publish a Markdown post to Quartz blog.")
    parser.add_argument("--title", required=True, help="Post title")
    parser.add_argument("--body", required=True, help="Post body markdown")
    parser.add_argument("--push", action="store_true", help="Push to GitHub after commit")
    args = parser.parse_args()

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(args.title)
    path = CONTENT_DIR / f"{today}-{slug}.md"

    if path.exists():
        now = datetime.now().strftime("%H%M%S")
        path = CONTENT_DIR / f"{today}-{slug}-{now}.md"

    markdown = f"""---
title: {args.title}
date: {today}
---

# {args.title}

{args.body}
"""

    path.write_text(markdown, encoding="utf-8")
    print(f"created: {path}")

    run(["git", "add", str(path.relative_to(ROOT))])

    commit_msg = f"Add post: {args.title}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=ROOT,
        text=True,
    )

    if result.returncode != 0:
        print("git commit failed or nothing to commit.")
        raise SystemExit(result.returncode)

    if args.push:
        run(["git", "push"])
        print("published: pushed to GitHub")
    else:
        print("committed only. Use --push to publish online.")


if __name__ == "__main__":
    main()
