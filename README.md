![agent-rules](https://p6junt15he.ufs.sh/f/dmguBujCxz5ET2DBH3HwfjWOvbPX62KwrE1ktysnpiMmaReY)

One canonical `AGENTS.md` file that powers all your AI coding agents via symlinks.

## Problem

Every AI coding agent has its own instruction file: Claude Code wants `CLAUDE.md`, Gemini CLI wants `GEMINI.md`, Codex wants `AGENTS.md`, and so on. Keeping them in sync manually is tedious and they inevitably drift apart.

## Solution

Maintain a single `AGENTS.md` at the root of this repo. A small Python harness creates symlinks from each agent's expected global path to this one file. Edit once, every agent picks it up.

## Supported agents

| Agent | Global instruction path | Link name |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `CLAUDE.md` |
| Codex (OpenAI) | `~/.codex/AGENTS.md` | `AGENTS.md` |
| Droid (Factory) | `~/.factory/AGENTS.md` | `AGENTS.md` |
| Amp | `~/.config/amp/AGENTS.md` | `AGENTS.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` | `AGENTS.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` | `GEMINI.md` |
| Intent (Augment) | `~/.augment/rules/global.md` | `global.md` |

Targets are defined in `harness/targets.json` and can be extended for new agents.

## Usage

### Check current state

```bash
python3 harness/sync.py check
```

Reports whether each agent's instruction file is correctly symlinked, missing, or pointing somewhere wrong.

### Preview changes

```bash
python3 harness/sync.py dry-run
```

Shows exactly what `sync` would do (create dirs, back up existing files, create symlinks) without touching anything.

### Apply

```bash
python3 harness/sync.py sync
```

Creates symlinks for all targets. Existing regular files are backed up with a `.bak` suffix before being replaced.

## Repo structure

```
agent-rules/
  AGENTS.md            # Canonical instructions (symlink target)
  README.md
  LICENSE              # MIT
  harness/
    sync.py            # The harness CLI (sync, check, dry-run)
    targets.json       # Agent target definitions
```

## Adding a new agent

1. Add an entry to `harness/targets.json` with the agent's global instruction path.
2. Run `python3 harness/sync.py dry-run` to verify.
3. Run `python3 harness/sync.py sync` to apply.

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## Acknowledgments

This project was inspired by and learned from several existing tools that tackle the same problem at different scales:

- **[amtiYo/agents](https://github.com/amtiYo/agents)** -- treats `AGENTS.md` as a canonical source and generates thin wrappers for other tools. The "one file to rule them all" philosophy directly shaped this project's approach.
- **[rule-porter](https://github.com/robinpellegrims/rule-porter)** -- a CLI that converts between Cursor `.mdc`, `AGENTS.md`, `CLAUDE.md`, and other formats. Its emphasis on warning about lossy conversions influenced the `check` and `dry-run` design here.
- **[rulesync](https://github.com/nicholasgriffintn/rulesync)** -- the most comprehensive tool in the space, supporting many agents and feature types. Studying its architecture helped define what to include in v1 and, just as importantly, what to leave out.

If you need bidirectional format conversion or full MCP/skills/hooks orchestration, those projects are worth a look. This repo intentionally stays minimal: one file, symlinks, done.

## License

MIT

---

![footer](https://p6junt15he.ufs.sh/f/dmguBujCxz5EQz9iGFyEwFq2hjMuRrzvNHSeYWoXmB4JlVb8)

<sub>*midjourney prompt: seven thin organic lines in different muted earth tones converging into a single bright point, topographic contour map aesthetic, matte paper texture, warm cream background with subtle grain, editorial illustration style, soft shadows, no text, horizontal composition — make the colors, like the waves, go into the central location, they all should slowly, at different paces, go to that central location*</sub>
