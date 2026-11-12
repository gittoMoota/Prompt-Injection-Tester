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