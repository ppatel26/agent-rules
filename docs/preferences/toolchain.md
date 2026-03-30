# Toolchain Preferences

Default tools and runtimes to use when the project does not already specify one.

## Python

- Use `uv` for environment setup, dependency management, and script running in fresh directories.
- Prefer `uv init`, `uv add`, and `uv run` over `pip`, `venv`, or `virtualenv`.

## JavaScript / TypeScript

- Use `bun` as the default package manager and runtime.
- Prefer `bun install`, `bun run`, and `bun add` over `npm` or `pnpm`.
- Exception: some frameworks (Next.js on Vercel, Cloudflare Wrangler) require `npm`. Use `npm` only when the framework explicitly does not support `bun`.

## General

- If a project already has a lockfile (`uv.lock`, `bun.lockb`, `package-lock.json`, etc.), follow the existing toolchain. Do not switch tools mid-project.
- When initializing a new project from scratch, use the preferred tools above.
