# AI Usage Note - Celare Project

## Date
June 8, 2026

## Project Name
Celare - PII Detector & Masker

## AI Model Used
Trae AI Assistant (Powered by Large Language Models)

---

## 1. System Prompt Strategy
We used iterative, role-based prompting:
- First, "DevOps Architect" for repository setup and Live Share config
- Next, "Python Data Engineer" for core engine development
- Then, "Git Deployment Specialist" for version control
- Finally, "UI Engineer & Technical Writer" for presentation layer

Each step built on the previous with clear requirements for output quality and file structure.

---

## 2. Structural Successes
- **Git Workflow**: Proper conventional commits, branch management, remote sync
- **Code Architecture**: Modular separation of data_ingestion, regex_engine, and app.py
- **Data Safety**: Strict .gitignore, encoding fallbacks, no hardcoded secrets
- **UI/UX**: Streamlit dashboard with side-by-side comparison, progress tracking, metrics

---

## 3. Edge-Case Errors & Fixes
- **Count Overcounting**: Initial mask_deterministic processed values twice; fixed by combining masking and counting in one loop
- **Regex Typo**: Missing closing parenthesis on email pattern; caught via py_compile syntax check
- **Git Divergence**: Local vs remote had different commits after VSIX removal; fixed with --force-with-lease

---

## 4. Human-in-the-Loop
All AI-generated code was reviewed for logic, security, and compliance. Git commit messages and project structure were manually validated.

## 5. Model Limitations
- No LLM-based PII detection (llm_engine.py stub remains for future Ollama integration
- Regex patterns can miss edge-case PII formats (addressed by upcoming Phase 2 LLM loop)
- No multi-language support yet
