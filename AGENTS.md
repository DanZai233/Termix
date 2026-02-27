# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Termix is a terminal-based cocktail mixing game (Python 3.8+, Textual TUI framework). It is a single-process, self-contained application with no external service dependencies (no database, no network, no Docker). See `README.md` for full feature description and keyboard controls.

### Running the app

- **Full TUI game**: `python3 main.py` (uses Textual framework, requires a terminal)
- **Demo version**: `python3 demo.py` (Rich-based console, interactive prompts — not suitable for non-interactive shells)
- **Config manager**: `python3 config_manager.py`

### Lint / Test

This project has no lint tool, test framework, or CI configuration. Use `python3 -m py_compile <file>` for syntax validation. All source files are under `src/` and the three entry points are at the repo root.

### Key caveats

- The Textual TUI (`main.py`) must be run in a real terminal; use the Desktop pane terminal or computerUse subagent for testing.
- `demo.py` uses `rich.prompt.Prompt.ask()` with `choices=` — it blocks on TTY input. Do not run it non-interactively.
- Game data lives in `config/` as JSON files (`ingredients.json`, `recipes.json`, `game_config.json`); no build step is needed.
- Dependencies are installed to user site-packages (`pip install --user`) since system site-packages is not writable in the cloud VM.
