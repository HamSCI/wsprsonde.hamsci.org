# {{PROJECT_NAME}}

## Project Overview
{{ONE-PARAGRAPH PROJECT DESCRIPTION — what is being written or built, its purpose, and audience.}}

**PI**: {{PI_NAME_AND_AFFILIATION}}
**Collaborators**: {{COLLABORATORS}}
**Funder**: {{FUNDER}}{{FUNDING_AMOUNT_OPTIONAL}}
**Project period**: {{PROJECT_PERIOD}}

## Project Goal
{{PROJECT_GOAL — 1-3 sentences.}}

## Repository Structure
This project starts from the `ai_project_template` scaffold. Add or remove top-level directories to match your project type. The scaffold expects:

```
{{REPO_NAME}}/
├── CLAUDE.md
├── README.md
├── .gitignore
├── .gitmodules                   ← present only if you add submodules
├── .claude/
│   ├── settings.json
│   ├── commands/commit.md        ← /commit workflow
│   └── rules/
│       ├── ai-governance.md
│       ├── latex-writing.md      ← delete if no LaTeX
│       └── python-code.md        ← delete if no Python
├── ai/
│   └── ai_usage_log.md           ← mandatory AI session log
└── {{PROJECT-SPECIFIC FOLDERS}}  ← e.g., manuscript/, src/, posters/, proposal/
```

## Submodules (optional)
If your project includes submodules (e.g., an Overleaf manuscript or a separate code repo):
1. Make changes and commit **inside** the submodule first
2. Then commit the updated submodule pointer in this repo
3. Always use `[AI-assisted]` prefix on commits made with AI assistance
4. Ask before pushing to any remote

The `/commit` workflow auto-detects submodules via `git submodule status`.

## AI Governance
All AI-assisted work must comply with the policies in `.claude/rules/ai-governance.md`.
Every substantive AI session must be logged in `ai/ai_usage_log.md` before committing.
Use the `/commit` command to handle logging and committing in the correct order.
