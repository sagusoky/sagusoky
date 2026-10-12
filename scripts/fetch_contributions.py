#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint (the same fragment the profile page itself uses) and
write data/contributions.json with raw days plus derived stats
(current streak, longest streak, best day, monthly totals).
No token, no auth, no GraphQL -- pure public HTML GitHub serves.
Runs locally and automatically via .github/workflows/update-profile-art.yml.
"""
import datetime
import json
import os
import re
import ssl
import subprocess
import sys

USERNAME = os.environ.get("GH_PROFILE_USER", "sagusoky")
URL = f"https://github.com/users/{USERNAME}/contributions"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "..", "data", "contributions.json")


def fetch_html():
    """Fetch HTML with requests, standard urllib, or curl as fallback."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # 1. Try requests if installed
    try:
        import requests
        resp = requests.get(URL, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass

    # 2. Try standard library urllib
    try:
        import urllib.request
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(URL, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.read().decode("utf-8")
    except Exception:
        pass

    # 3. Fallback to system curl
    try:
        cmd = ["curl", "-sL", "-A", headers["User-Agent"], URL]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
        return result.stdout
    except Exception as e:
        print(f"Error fetching {URL}: {e}", file=sys.stderr)
        sys.exit(1)


def parse_days(html):
    """Parse days using BeautifulSoup if available, or regex fallback."""
    days = []
    tooltips = {}

    # Extract all tooltips: id or for attribute mapping to text
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>', html, re.DOTALL):
        target_id = m.group(1).strip()
        tip_text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        tooltips[target_id] = tip_text

    # Extract all contribution day cells
    # Matches <td ... data-date="2026-xx-xx" ... data-level="X" ... id="..." ...>
    td_matches = re.finditer(r'<td\b([^>]*)>', html, re.DOTALL)
    for td in td_matches:
        attrs_str = td.group(1)
        if 'ContributionCalendar-day' not in attrs_str and 'data-date' not in attrs_str:
            continue

        date_m = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', attrs_str)
        if not date_m:
            continue
        date_str = date_m.group(1)

        level_m = re.search(r'data-level="(\d+)"', attrs_str)
        level = int(level_m.group(1)) if level_m else 0

        id_m = re.search(r'id="([^"]+)"', attrs_str)
        cell_id = id_m.group(1) if id_m else ""

        tooltip_text = tooltips.get(cell_id, "")
        if re.search(r'no contributions', tooltip_text, re.IGNORECASE):
            count = 0
        else:
            cm = re.match(r'(\d+)', tooltip_text)
            if cm:
                count = int(cm.group(1))
            else:
                # If tooltip not matched, extrapolate count from level
                count = max(level, 1) if level > 0 else 0

        days.append({
            "date": date_str,
            "count": count,
            "level": level,
            "id": cell_id
        })

    days.sort(key=lambda d: d["date"])
    return days


def compute_current_streak(days):
    if not days:
        return 0, None, None
    idx = len(days) - 1
    # If today has 0 contributions so far, check if streak continued until yesterday
    if days[idx]["count"] == 0 and idx > 0:
        idx -= 1
    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    start_idx = idx + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days):
    longest = run = 0
    longest_start = longest_end = None
    run_start_idx = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = days[i]["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days):
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"]) if days else {"date": None, "count": 0}
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"] if days else None, "end": days[-1]["date"] if days else None},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


def main():
    print(f"Fetching contribution data for @{USERNAME}...")
    html = fetch_html()
    days = parse_days(html)
    if not days:
        print("Warning: no contribution day cells found. Checking markup...", file=sys.stderr)
        sys.exit(1)

    data = build_data(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Successfully generated {OUT_PATH}:")
    print(f"  - Total contributions: {data['total_contributions']}")
    print(f"  - Days captured: {len(data['days'])}")
    print(f"  - Current streak: {data['current_streak']['length']} days")
    print(f"  - Longest streak: {data['longest_streak']['length']} days")
    print(f"  - Best day: {data['best_day']['date']} ({data['best_day']['count']} contributions)")


if __name__ == "__main__":
    main()
