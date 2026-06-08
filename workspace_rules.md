# Workspace Rules for PII Detector and Masker

## 1. AI Agent File Assignment
- **AI agents must only modify the specific file assigned to their user**:
  - File assignments are to be determined by the team lead and documented here.
  - No cross-file modifications allowed without explicit team approval.

## 2. Git Commit Requirements
- **All commit messages must include "Co-authored-by" tags** for all contributors to the change.
- Example commit message format:
  ```
  Add regex pattern for passport numbers

  Co-authored-by: Developer 1 <dev1@example.com>
  Co-authored-by: Developer 2 <dev2@example.com>
  ```

## 3. Code Quality Standards
- Follow PEP 8 style guidelines for Python code.
- Include docstrings for all functions and classes.
- Write unit tests for new functionality.

## 4. Security Guidelines
- Never commit sensitive data or PII to the repository.
- Use environment variables for API keys and secrets.
- All data files must be excluded via .gitignore.
