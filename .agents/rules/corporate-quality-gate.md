---
trigger: always_on
description: Corporate Engineering Quality Gate and Shift-Left Governance
---
# Corporate Engineering Quality Gate

This project adheres to the **Corporate Software Engineer Framework** and **ECC Quality Standards**.

## Mandatory Verification Commands
- **Unit & Property Tests**: `pytest`
- **Linting & Code Style**: `ruff check .`
- **Static Type Checking**: `mypy .`
- **Secret & Credential Scan**: `python .agents/skills/corp-pipeline/scripts/secret_scanner.py .`

## Engineering Invariants
1. **Shift-Left TDD**: For any bug fix or feature addition, write failing tests first (`tests/`), then implement minimal code to reach green.
2. **Pydantic V2 & Strong Typing**: Models in `src/corporate_engineer/models.py` must use strict Pydantic v2 validation.
3. **Architecture Decisions**: Major structural changes require an ADR in `docs/adr/ADR-<NUM>-<slug>.md`.
4. **Pre-Flight Gate**: Never commit or submit changes before running `ruff check .`, `mypy .`, `pytest`, and `secret_scanner.py`.
5. **Conventional Commits**: Commits must follow `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, or `chore:`.
