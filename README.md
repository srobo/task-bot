# SR Task Bot

![](https://github.com/RealOrangeOne/sr-task-bot/workflows/Tests/badge.svg)
![](https://github.com/RealOrangeOne/sr-task-bot/workflows/Execute/badge.svg)

This bot is designed to print tasks into our Slack, so we can monitor progress on things. Whilst it was originally designed for the [Tasks](https://github.com/srobo/tasks/issues) repo, it can be used for anything.

## Installation

For local development, set up a virtual environment, and install the contents of `dev-requirements.txt`.


## Execution

The script itself, `task-bot.py` takes a single argument of the repo you want to use (ie `srobo/tasks`).

The actual bot itself runs through GitHub Actions, to avoid the need for a server or manual deployment. Settings for this can be found in `.github/workflows/execute.yml`.
