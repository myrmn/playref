# PlayRef: AI IDE Prompt Pack

How to use this pack with Cursor / Windsurf / Claude Code / Copilot / any AI IDE.

## Setup (5 minutes)

1. Create an empty repo folder `playref/`.
2. Copy this pack into it so you have:
   ```
   playref/
   ├── AGENTS.md              <- master rules (see tool-specific copy below)
   ├── .env.example
   ├── docs/
   │   ├── PROJECT_SPEC.md
   │   ├── ROADMAP.md
   │   ├── PROGRESS.md
   │   └── API_CONTRACTS.md   <- YOU fill this in (endpoints, keys, formats)
   └── prompts/               <- paste these into the IDE chat
   ```
3. Tool-specific rules file (same content as `AGENTS.md`):
   - Cursor: copy to `.cursor/rules/playref.mdc` (add frontmatter `alwaysApply: true`) or `.cursorrules`
   - Claude Code: copy to `CLAUDE.md`
   - Windsurf: `.windsurfrules`
   - Others: keep `AGENTS.md` and tell the agent to read it first
4. Put the IFAB Laws of the Game PDF at `data/raw/laws_of_the_game.pdf` (latest edition).
   Optional: VAR protocol PDF at `data/raw/var_protocol.pdf`.
5. Fill in `docs/API_CONTRACTS.md` and copy `.env.example` to `.env`.

## Workflow

1. Paste `prompts/00_kickoff.md` into the IDE. The agent reads everything, confirms understanding, and asks you questions before coding.
2. Answer, then paste `prompts/phase_1.md`.
3. When the phase finishes, the agent **stops, shows a report, and asks for approval**.
4. Reply with `approved` (or list changes). Then paste `prompts/phase_transition.md` followed by the next phase file, or just say "approved, go to phase N" since the agent has the files.
5. Repeat through Phase 6.

## Helper prompts

| File | Use when |
|---|---|
| `prompts/phase_transition.md` | Moving to the next phase after approval |
| `prompts/util_resume_session.md` | Starting a new chat/session mid-project |
| `prompts/util_debug.md` | Something is broken |
| `prompts/util_review.md` | You want a code/quality review before approving a phase |
| `prompts/util_eval_run.md` | Running the evaluation suite |

## Tips

- One phase per chat session keeps context clean. Use `util_resume_session.md` to restart.
- Never let the agent skip the gate. If it does, paste: "Stop. Re-read AGENTS.md section 'Phase Gate Protocol'."
- Commit to git at the end of every phase (the agent will propose a commit message).
