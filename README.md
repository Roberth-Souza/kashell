[![progress-banner](https://backend.codecrafters.io/progress/shell/b896c72a-c500-4fe7-bfec-c1f347020dd5)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

# kashell

A POSIX-ish shell written from scratch in Python, with no external dependencies.

This is my solution to the ["Build Your Own Shell"](https://app.codecrafters.io/courses/shell/overview)
challenge by [CodeCrafters](https://codecrafters.io) — the challenge, its stages
and the test suite are theirs. This is a learning project, built stage by stage.

Along the way: shell command parsing, REPLs, `PATH` lookup and builtin commands.

**Note**: if you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to try the challenge yourself.

## What works

- Builtins: `exit`, `echo`, `type`, `pwd`, `cd` (supports `~`)
- Running external programs found in `PATH`
- Quoting: single quotes, double quotes and backslash escapes

## Running it

1. Make sure you have [`uv`](https://docs.astral.sh/uv/) installed
2. Run `./your_program.sh`
