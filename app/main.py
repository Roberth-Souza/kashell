"""kashell — a POSIX-ish shell written from scratch, with no dependencies."""

import subprocess
import sys
from typing import TextIO

from app.handlers import built_ins
from app.path import find_executable
from app.tokenizer import (
    Token,
    TokenizerState,
    tokenizer,
)


def receive_command():
    state = TokenizerState()
    _ = sys.stdout.write("$ ")
    command = input()

    if not command or not command.strip():
        return None

    state = tokenizer(command, state)
    while state.unfinished:
        print("> ", end="")
        command = input()
        state = tokenizer(command, state)

    return state


def split_redirect(tokens: list[Token]) -> tuple[list[str], str | None]:
    """Pull the redirection out of the token list.

    The operator and the token right after it are consumed wherever they
    appear, so `> out.txt echo hi` yields `(["echo", "hi"], "out.txt")`.
    """

    words: list[str] = []
    target: str | None = None

    # The operator marks the *next* token as the file, same idea as `escaping`
    # marking the next character in the tokenizer
    expecting_target = False

    for token in tokens:
        if expecting_target:
            target = token.text
            expecting_target = False

        elif token.operator:
            expecting_target = True

        else:
            words.append(token.text)

    return words, target


def run_command(cmd_split: list[str], sink: TextIO) -> None:
    """Dispatch one command to a builtin or to an executable on PATH.

    Everything it prints goes to `sink`, which is either `sys.stdout` or the
    file opened for a redirection.
    """

    cmd_name = cmd_split[0]
    args = cmd_split[1:]

    handler = built_ins.get(cmd_name)
    if handler is not None:
        handler(args, sink)
        return

    exec_path = find_executable(cmd_name)
    if exec_path is not None:
        _ = subprocess.run(cmd_split, executable=exec_path, check=False, stdout=sink)
        return

    print(f"{cmd_name}: command not found", file=sys.stderr)


def main():
    """The REPL: read a line, tokenize it, dispatch to a builtin or to PATH."""

    while True:
        state = receive_command()
        if state is None:
            continue

        tokens = state.tokens

        if not tokens:
            continue

        # Everything downstream (builtins, subprocess) speaks plain strings
        cmd_split, redirect_target = split_redirect(tokens)

        if redirect_target is None:
            if cmd_split:
                run_command(cmd_split, sys.stdout)
            continue

        # Write mode truncates the file even when there is no command to run
        with open(redirect_target, "w") as sink:
            if cmd_split:
                run_command(cmd_split, sink)


if __name__ == "__main__":
    main()
