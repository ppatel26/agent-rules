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
  docs/
    guides/
    principles/
  harness/
    sync.py            # The harness CLI (sync, check, dry-run)
    targets.json       # Agent target definitions
```

## Canonical `AGENTS.md` design

This repo is intentionally opinionated. It does not claim there is one universally correct way to write a canonical agent instruction file.

Our current design is:

- keep the root `AGENTS.md` short and universal
- keep deeper rationale in `docs/`
- use triggered references in the root file: `read X when Y`
- prefer more specific guidance over more general guidance

This shape is based on how current tools actually work in practice. Different agents support deeper context through different mechanisms: hierarchical instruction files, imports, rules, `@` references, and skills. The common pattern is the same: keep the always-on guidance small, and load deeper guidance only when the task makes it relevant.

That is why this repo does not try to cram every preference into one giant `AGENTS.md`. The canonical file is the default operating layer; the docs are supporting layers.

This repo is also a public working notebook for the harness itself. As agents get better at scoped loading, delegation, and tool use, both the sync harness and the canonical-file pattern may evolve.

### `docs/` is optional

You do not have to structure your canonical instructions the way this repo does.

If you want the simplest possible setup, keep everything in a single `AGENTS.md` file and leave `docs/` empty or omit it entirely. The harness still works fine in that mode: one canonical file, many symlinked agent instruction files.

The `docs/` layout exists because it works well for this repo's preferences and research process, not because it is required by the harness.

### Current working rules

- put non-negotiable rules in `AGENTS.md`
- put deeper rationale, examples, and taste in `docs/`
- use explicit triggered references instead of a bare link dump
- do not assume every tool auto-loads referenced files
- when guidance conflicts, the more specific relevant guidance wins

### Research references

These informed the current structure:

- Claude Code memory and project instructions: <https://docs.anthropic.com/en/docs/claude-code/memory>
- Codex `AGENTS.md`: <https://developers.openai.com/codex/guides/agents-md>
- Codex skills: <https://developers.openai.com/codex/skills>
- Gemini CLI `GEMINI.md`: <https://geminicli.com/docs/cli/gemini-md/>
- Gemini import processor: <https://geminicli.com/docs/reference/memport/>
- Cursor rules: <https://cursor.com/docs/rules>
- Cursor skills: <https://cursor.com/docs/skills>
- Amp manual: <https://ampcode.com/manual>
- OpenCode rules: <https://opencode.ai/docs/rules/>
- OpenCode skills: <https://opencode.ai/docs/skills/>
- Factory `AGENTS.md`: <https://docs.factory.ai/cli/configuration/agents-md>
- Factory skills: <https://docs.factory.ai/cli/configuration/skills>
- Augment guidelines: <https://docs.augmentcode.com/setup-augment/guidelines>
- Augment CLI rules: <https://docs.augmentcode.com/cli/rules>

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
