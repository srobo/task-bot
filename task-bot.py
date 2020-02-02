from github import Github
import sys
from math import floor
from datetime import datetime

def main():
    github = Github()
    repo = github.get_repo(sys.argv[1])
    messages = []
    now = datetime.now()
    for milestone in repo.get_milestones():
        percentage_complete = round((milestone.closed_issues / (milestone.open_issues + milestone.closed_issues)) * 100)
        message = f"{milestone.title}: {percentage_complete}% complete."
        if milestone.due_on:
            duration = milestone.due_on - milestone.created_at
            remaining = milestone.due_on - now
            time_used = round((remaining.days / duration.days) * 100)
            message += f" Due {milestone.due_on.date().isoformat()}. {remaining.days} days remaining. {time_used}% time used."
        messages.append(message)
    print("\n".join(messages))


if __name__ == '__main__':
    main()
