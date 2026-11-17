# Progress log

## Step 1: project skeleton
- Created virtual environment and base folder layout
- Added pyproject.toml with dependencies
- Added class diagram to docs
- Next: data models

## Step 2: data models
- Added AttackCase, Verdict, Result and Report in models.py
- Report calculates leak count and pass rate, excluding errored attacks
- Added unit tests (pytest) and linted with ruff
- Next: attack library (YAML loader)


## Step 3: attack library
- Added AttackLibrary to load attack cases from YAML files
- Bundled 15 starter attacks across 5 categories
- Added filtering by category and minimum severity, plus validation errors
- Added unit tests, including a test for the bundled payloads
- Next: demo vulnerable chatbot


## Step 4: demo vulnerable chatbot
- Added a keyword-based FastAPI chatbot with a hidden canary secret
- Vulnerable mode leaks to every bundled attack; hardened mode (BOT_HARDENED=1) refuses most but still leaks via encoding tricks
- Added unit tests, including a check that the bot reacts to every bundled attack
- Next: HTTP target and canary detector


## Step 5: HTTP target and canary detector
- Added Target and Detector interfaces
- Added HttpTarget to send prompts to any JSON chat endpoint, with clear errors
- Added CanaryDetector that finds the secret in plain, separated, reversed, rot13, hex and base64 forms
- Added unit tests and an integration test: every bundled attack leaks from the vulnerable bot, and only the encoding attacks leak from the hardened bot
- Next: runner


## Step 6: runner
- Added Runner that sends each attack to a target, asks the detector for a verdict and builds a Report
- Target errors are recorded in the report and the run continues
- Added an optional callback so the command line can show progress
- Added unit tests with a fake target and integration tests against the demo bot (vulnerable: 15 of 15 leaks, hardened: 3 of 15)
- Next: JSON and HTML reporters


## Step 7: JSON and HTML reporters
- Added a Reporter interface with JsonReporter and HtmlReporter
- Reports show the pass rate, a per-category summary and every attack with its reply and evidence
- HTML output escapes target replies, because replies are untrusted text
- Added a script that scans the demo bot and writes sample reports
- Renamed tests/intergration to tests/integration
- Next: command-line interface


## Step 8: command-line interface
- Added `promptprobe scan` (filters, custom field names, headers, report format, fail-on-leak exit code) and `promptprobe attacks`
- Exit codes: 0 ok, 1 leaks found with --fail-on-leak, 2 usage or connection error
- Added CLI tests using Typer's test runner and fake targets
- Next: GitHub Actions CI


## Step 9: GitHub Actions CI
- Added a workflow that installs the project, runs ruff and pytest on Python 3.11 and 3.13 for every push and pull request
- Raised the minimum Python version to 3.11
- Next: README and limitations document


## Step 10: README and limitations
- Wrote the README with quick start, options, example results, design diagram and responsible-use note
- Added docs/limitations.md
- Next: real AI target