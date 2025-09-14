# Feature SW 5.0
Feature customizations built conceptually on Base 1.0:
- wider default, height clamp, logging in camera init
- Median() metric
- tighter telemetry interval with tags
- JSON tweaks for RVC (timeout, exposure, log_level)

Make all scripts executable:
- chmod +x tools/build.sh tools/test.sh tools/run_checks.py

Git commit & tag:
- git add -A
- git commit -m "seed: Feature SW 5.0 over Base 1.0 semantics"
- git tag -a feature/v5.0 -m "Feature SW 5.0"
