#!/usr/bin/env python3

import argparse
import os
from datetime import datetime
from math import floor

import requests
from github import Github, Milestone


def as_percentage(a: float, b: float) -> int:
    return floor((a / b) * 100)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=str)
    return parser.parse_args()


def process_milestone(milestone: Milestone) -> str:
    now = datetime.now()
    html_url = milestone._rawData["html_url"]
    segments = []
    total_issues = milestone.open_issues + milestone.closed_issues
    percentage_complete = as_percentage(milestone.closed_issues, total_issues)
    segments.append(
        f":heavy_check_mark: {percentage_complete}% completed ({milestone.closed_issues}/{total_issues})"
    )
    if milestone.due_on:
        duration = milestone.due_on - milestone.created_at
        remaining = milestone.due_on - now
        time_used = as_percentage(remaining.days, duration.days)
        segments += [
            f":date: {milestone.due_on.date().isoformat()}",
            f":alarm_clock: {time_used}% time used",
        ]
    merged_segments = "\n".join(["\t" + segment for segment in segments]) + "\n"
    return f"<{html_url}|{milestone.title}>\n" + merged_segments


def main() -> None:
    args = parse_args()
    github = Github(os.environ.get("GITHUB_TOKEN"))
    repo = github.get_repo(args.repo)
    messages = [
        process_milestone(milestone) for milestone in repo.get_milestones(sort="due_on")
    ]
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        response = requests.post(
            webhook_url,
            json={
                "text": "*Task Status*",
                "attachments": [{"text": message} for message in messages],
            },
        )
        response.raise_for_status()
    print("\n".join(messages))


if __name__ == "__main__":
    main()
