import os
import sys
from datetime import datetime
from math import floor

import requests
from github import Github


def main() -> None:
    github = Github(os.environ.get("GITHUB_TOKEN"))
    repo = github.get_repo(sys.argv[1])
    messages = []
    now = datetime.now()
    for milestone in repo.get_milestones(sort="due_on"):
        html_url = milestone._rawData["html_url"]
        segments = []
        total_issues = milestone.open_issues + milestone.closed_issues
        percentage_complete = floor((milestone.closed_issues / total_issues) * 100)
        segments.append(
            f":heavy_check_mark: {percentage_complete}% completed ({milestone.closed_issues}/{total_issues})"
        )
        if milestone.due_on:
            duration = milestone.due_on - milestone.created_at
            remaining = milestone.due_on - now
            time_used = round((remaining.days / duration.days) * 100)
            segments += [
                f":date: {milestone.due_on.date().isoformat()}",
                f":alarm_clock: {time_used}% time used",
            ]
        merged_segments = "\n".join(["\t" + segment for segment in segments]) + "\n"
        messages.append(f"<{html_url}|{milestone.title}>\n" + merged_segments)
    print("\n".join(messages))
    response = requests.post(
        os.environ["SLACK_WEBHOOK_URL"],
        json={"text": "*Task Status*", "attachments": [{"text": "\n".join(messages)}]},
    )
    response.raise_for_status()


if __name__ == "__main__":
    main()
