"""kashell — a POSIX-ish shell written from scratch, with no dependencies."""

import subprocess
import sys

from app.handlers import built_ins
from app.path import find_executable
from app.tokenizer import (
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


def main():
    """The REPL: read a line, tokenize it, dispatch to a builtin or to PATH."""

    while True:
        state = receive_command()
        if state is None:
            continue

        cmd_split = state.tokens

        if not cmd_split:
            continue

        cmd_name = cmd_split[0]
        args = cmd_split[1:]

        handler = built_ins.get(cmd_name)
        if handler is not None:
            handler(args)

        elif (exec_path := find_executable(cmd_name)) is not None:
            _ = subprocess.run(cmd_split, executable=exec_path, check=False)

        else:
            print(f"{cmd_name}: command not found")
            continue


if __name__ == "__main__":
    main()
