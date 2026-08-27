"""kashell — a POSIX-ish shell written from scratch, with no dependencies."""

import subprocess
import sys
from typing import Literal, NamedTuple, TextIO

from app.handlers import built_ins
from app.path import find_executable
from app.tokenizer import (
    Token,
    TokenizerState,
    tokenizer,
)


class Redirect(NamedTuple):
    """target: the file to redirect to, fd: 1 for stdout, 2 for stderr"""

    target: str | None
    fd: int = 1
    mode: Literal["w", "a"] = "w"  # Can be "a" for append


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


def split_redirect(tokens: list[Token]) -> tuple[list[str], Redirect]:
    """Pull the redirection out of the token list.

    The operator and the token right after it are consumed wherever they
    appear, so `> out.txt echo hi` yields `(["echo", "hi"], "out.txt")`.
    """

    words: list[str] = []
    redirect = Redirect(None, 1, "w")

    # The operator marks the *next* token as the file, same idea as `escaping`
    # marking the next character in the tokenizer
    expecting_target = 0
    append_write = "w"

    for token in tokens:
        if expecting_target:
            redirect = Redirect(
                target=token.text, fd=expecting_target, mode=append_write
            )
            expecting_target = 0
            append_write = "w"

        elif token.operator:
            if token.text[0] == "2":
                expecting_target = 2
                if token.text == "2>>":
                    append_write = "a"
            else:
                expecting_target = 1
                if token.text == "1>>" or token.text == ">>":
                    append_write = "a"
        else:
            words.append(token.text)

    return words, redirect


def run_command(cmd_split: list[str], out: TextIO, err: TextIO) -> None:
    """Dispatch one command to a builtin or to an executable on PATH.

    Everything it prints goes to either out or err ( stdout / stderr )
    so that we can redirect it to a file if the user requested it.
    """

    cmd_name = cmd_split[0]
    args = cmd_split[1:]

    handler = built_ins.get(cmd_name)
    if handler is not None:
        handler(args, out, err)
        return

    exec_path = find_executable(cmd_name)
    if exec_path is not None:
        _ = subprocess.run(
            cmd_split, executable=exec_path, check=False, stdout=out, stderr=err
        )
        return

    print(f"{cmd_name}: command not found", file=err)


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

        if redirect_target.target is None:
            if cmd_split:
                run_command(cmd_split, sys.stdout, sys.stderr)
            continue

        with open(redirect_target.target, redirect_target.mode) as sink:
            out, err = sys.stdout, sys.stderr

            if redirect_target.fd == 2:
                err = sink
            else:
                out = sink

            if cmd_split:
                run_command(cmd_split, out, err)


if __name__ == "__main__":
    main()
