"""kashell — a POSIX-ish shell written from scratch, with no dependencies."""

import os
import subprocess
import sys

from app.tokenizer import (
    Tokenizer_State,
    tokenizer,
)

built_ins = {"exit", "type", "echo", "pwd", "cd"}


def find_executable(cmd_name: str) -> str | None:
    """Checks all directories in PATH in search for an executable"""

    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(os.pathsep):
        full_path = os.path.join(directory, cmd_name)

        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path

    return None


def check_in_builtins(target: str) -> bool:
    return target in built_ins


def handle_type(target: str) -> str:

    if check_in_builtins(target):
        return f"{target} is a shell builtin"

    else:
        find = find_executable(target)
        if find is not None:
            return f"{target} is {find}"
        return f"{target}: not found"


def current_directory() -> str:
    return os.getcwd()


def change_directory(path: str):
    """Change to path directory if it exists"""

    target = os.path.expanduser(path)
    if os.path.isdir(target):
        os.chdir(target)
        return

    raise ValueError(f"cd: {path}: No such file or directory")


def receive_command():
    state = Tokenizer_State()
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

        if cmd_name == "echo":
            print(" ".join(args))

        elif cmd_name == "type":
            if not args:
                continue

            result = handle_type(args[0])
            print(result)

        elif cmd_name == "pwd":
            print(current_directory())

        elif cmd_name == "cd":
            if not args:
                change_directory("~")

            else:
                try:
                    change_directory(args[0])
                except ValueError as err:
                    print(err)

        elif cmd_name == "exit":
            break

        elif (exec_path := find_executable(cmd_name)) is not None:
            _ = subprocess.run(cmd_split, executable=exec_path, check=False)

        else:
            print(f"{cmd_name}: command not found")
            continue


if __name__ == "__main__":
    main()
