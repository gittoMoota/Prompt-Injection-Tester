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