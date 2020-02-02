from github import Github
import sys
from math import floor

def main():
    github = Github()
    repo = github.get_repo(sys.argv[1])
    for milestone in repo.get_milestones():
        percentage_complete = (milestone.closed_issues / (milestone.open_issues + milestone.closed_issues)) * 100
        print(milestone.title, floor(percentage_complete), milestone.open_issues, milestone.closed_issues)

if __name__ == '__main__':
    main()
