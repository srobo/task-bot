#!/usr/bin/env python3

import argparse
import os
from datetime import datetime
from math import floor
from typing import Optional

import requests
from github import Github, Milestone, Repository
from github.Label import Label


def as_percentage(a: float, b: float) -> int:
    if b == 0:
        return 0
    return floor((a / b) * 100)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=str)
    return parser.parse_args()


def get_in_progress_label(repo: Repository) -> Optional[Label]:
    for label in repo.get_labels():
        if "in progress" in label.name.lower():
            return label
    return None


def get_blocked_label(repo: Repository) -> Optional[Label]:
    for label in repo.get_labels():
        if "blocked" in label.name.lower():
            return label
    return None


def process_milestone(
    repo: Repository,
    milestone: Milestone,
    in_progress_label: Optional[Label],
    blocked_label: Optional[Label],
) -> str:
    now = datetime.now()
    html_url = milestone._rawData["html_url"]
    total_issues = milestone.open_issues + milestone.closed_issues
    percentage_complete = as_percentage(milestone.closed_issues, total_issues)

    detail_lines = []

    status_line = f":heavy_check_mark: {percentage_complete}% completed"
    if in_progress_label:
        in_progress_issues = list(
            repo.get_issues(
                milestone=milestone, labels=[in_progress_label], state="open"
            )
        )
        if in_progress_issues:
            percentage_in_progress = as_percentage(
                len(in_progress_issues), total_issues
            )
            status_line += (
                f" - :hourglass_flowing_sand: {percentage_in_progress}% in progress"
            )
    if blocked_label:
        blocked_issues = list(
            repo.get_issues(milestone=milestone, labels=[blocked_label], state="open")
        )
        if blocked_issues:
            percentage_blocked = as_percentage(len(blocked_issues), total_issues)
            status_line += f" - :octagonal_sign: {percentage_blocked}% blocked"
    detail_lines.append(status_line)

    if milestone.due_on:
        duration = milestone.due_on - milestone.created_at
        remaining = milestone.due_on - now
        time_used = 100 - as_percentage(remaining.days, duration.days)
        detail_lines.append(
            f":date: {milestone.due_on.date().isoformat()} - :alarm_clock: {time_used}% time used"
        )

    rendered_line = (
        f"<{html_url}|{milestone.title}> - {milestone.closed_issues}/{total_issues}"
    )
    for line in detail_lines:
        rendered_line += f"\n\t{line}"

    return rendered_line


def main() -> None:
    args = parse_args()
    github = Github(os.environ.get("GITHUB_TOKEN"))
    repo = github.get_repo(args.repo)
    in_progress_label = get_in_progress_label(repo)
    blocked_label = get_blocked_label(repo)
    messages = [
        process_milestone(repo, milestone, in_progress_label, blocked_label)
        for milestone in repo.get_milestones(sort="due_on")
    ]
    if not messages:
        return
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    title = f"*Task Status for <{repo.html_url}|{repo.full_name}>*"
    if webhook_url:
        response = requests.post(
            webhook_url,
            json={
                "text": title,
                "attachments": [{"text": message} for message in messages],
            },
        )
        response.raise_for_status()
    print(title)
    print("\n".join(messages))


if __name__ == "__main__":
    main()
