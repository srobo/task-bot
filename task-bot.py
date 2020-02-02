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
    detail_line = ""
    total_issues = milestone.open_issues + milestone.closed_issues
    percentage_complete = as_percentage(milestone.closed_issues, total_issues)
    if milestone.due_on:
        duration = milestone.due_on - milestone.created_at
        remaining = milestone.due_on - now
        time_used = as_percentage(remaining.days, duration.days)
        detail_line += f":date: {milestone.due_on.date().isoformat()} - :alarm_clock: {time_used}% time used"

    return "\n".join(
        [
            f"<{html_url}|{milestone.title}> - {percentage_complete}% completed :heavy_check_mark: ({milestone.closed_issues}/{total_issues})",
            "\t" + detail_line,
        ]
    )


def main() -> None:
    args = parse_args()
    github = Github(os.environ.get("GITHUB_TOKEN"))
    repo = github.get_repo(args.repo)
    messages = [
        process_milestone(milestone) for milestone in repo.get_milestones(sort="due_on")
    ]
    if not messages:
        return
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
