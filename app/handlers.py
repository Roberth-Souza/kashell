"""Shell builtins and the dispatch table that maps a name to its handler."""

import os
import sys
from typing import TextIO

from app.path import find_executable


def check_in_builtins(target: str) -> bool:
    return target in built_ins


def handle_type(args: list[str], sink: TextIO) -> None:

    if not args:
        return

    if check_in_builtins(args[0]):
        print(f"{args[0]} is a shell builtin", file=sink)

    else:
        find = find_executable(args[0])
        if find is not None:
            print(f"{args[0]} is {find}", file=sink)
        else:
            # Errors go to stderr, so `> file` never captures them
            print(f"{args[0]}: not found", file=sys.stderr)


def current_directory() -> str:
    return os.getcwd()


def change_directory(path: str):
    """Change to path directory if it exists"""

    target = os.path.expanduser(path)
    if os.path.isdir(target):
        os.chdir(target)
        return

    raise ValueError(f"cd: {path}: No such file or directory")


def handle_echo(args: list[str], sink: TextIO):
    print(" ".join(args), file=sink)


def handle_pwd(_args: list[str], sink: TextIO):
    print(current_directory(), file=sink)


def handle_cd(args: list[str], _sink: TextIO):
    if not args:
        change_directory("~")

    else:
        try:
            change_directory(args[0])
        except ValueError as err:
            print(err, file=sys.stderr)


def handle_exit(args: list[str], _sink: TextIO):
    sys.exit(int(args[0]) if args else 0)


built_ins = {
    "exit": handle_exit,
    "type": handle_type,
    "echo": handle_echo,
    "pwd": handle_pwd,
    "cd": handle_cd,
}
