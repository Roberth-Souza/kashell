import os
import sys
import subprocess
from enum import Enum
from typing import NamedTuple

built_ins = {"exit", "type", "echo", "pwd", "cd"}

DOUBLE_QUOTE_ESCAPABLE = {"$", "`", '"', "\\", "\n"}


class Verdict(Enum):
    """What the tokenizer should do with the current character"""

    ACCUMULATE = "accumulate"
    FLUSH = "flush"
    SKIP = "skip"


class Result(NamedTuple):
    verdict: Verdict
    quote_type: str | None = None
    escaping: bool = False
    text: str = ""


class Tokenizer_State(NamedTuple):
    buffer: list[str] | None = None
    quote_type: str | None = None
    escaping: bool = False
    tokens: list[str] | None = None
    unfinished: bool = False


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


def classify_character(char: str, quote_type: str | None, escaping: bool) -> Result:
    """Return the action, the text to emit, and the updated state"""

    # This only runs on the next char after founding a backslash
    if escaping:
        if quote_type == '"' and char not in DOUBLE_QUOTE_ESCAPABLE:
            return Result(
                Verdict.ACCUMULATE,
                quote_type=quote_type,
                escaping=False,
                text="\\" + char,
            )

        # We are escaping, but not inside double quotes or the char is double_quote_escapable
        return Result(
            Verdict.ACCUMULATE, quote_type=quote_type, escaping=False, text=char
        )

    # At this point we are no longer escaping
    # So if we find a backslash, we check if quote_type is single quote
    # Because backslashes are treated literally inside single quotes

    elif char == "\\" and quote_type != "'":
        # backslash when quotes are None or double
        return Result(Verdict.SKIP, quote_type=quote_type, escaping=True)

    elif char in ("'", '"'):
        if quote_type is None:  # Opening quote
            return Result(Verdict.SKIP, quote_type=char, escaping=False)
        elif char == quote_type:  # Closing quote
            return Result(Verdict.SKIP, quote_type=None, escaping=False)

        # else is another quote type inside quoted:
        return Result(
            Verdict.ACCUMULATE, quote_type=quote_type, escaping=False, text=char
        )

    elif char == " " and quote_type is None:
        return Result(Verdict.FLUSH, quote_type=quote_type, escaping=False)

    return Result(Verdict.ACCUMULATE, quote_type=quote_type, escaping=False, text=char)


def tokenizer(command: str, state: Tokenizer_State) -> Tokenizer_State:
    quote_type = state.quote_type
    escaping = state.escaping
    buffer = state.buffer or []  # If state.buffer is None, the buffer resets
    tokens = state.tokens or []  # Same here but for Tokens

    for char in command:
        verdict, quote_type, escaping, text = classify_character(
            char, quote_type, escaping
        )

        if verdict is Verdict.SKIP:
            continue

        elif verdict is Verdict.ACCUMULATE:
            buffer.append(text)

        else:
            if buffer:
                tokens.append("".join(buffer))
                buffer = []
            continue

    if escaping:
        return Tokenizer_State(
            buffer=buffer,
            tokens=tokens,
            quote_type=quote_type,
            escaping=escaping,
            unfinished=True,
        )

    if buffer:
        tokens.append("".join(buffer))
    return Tokenizer_State(
        buffer=buffer,
        tokens=tokens,
        quote_type=quote_type,
        escaping=escaping,
        unfinished=False,
    )


def main():

    while True:
        state = Tokenizer_State()
        _ = sys.stdout.write("$ ")
        command = input()

        if not command or not command.strip():
            continue

        state = tokenizer(command, state)
        while state.unfinished:
            print("> ")
            command = input()
            state = tokenizer(command, state)

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
            _ = subprocess.run(cmd_split, executable=exec_path)

        else:
            print(f"{cmd_name}: command not found")
            continue


if __name__ == "__main__":
    main()
