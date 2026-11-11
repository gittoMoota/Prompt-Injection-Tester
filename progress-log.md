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