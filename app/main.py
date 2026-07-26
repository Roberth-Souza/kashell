"""kashell — a POSIX-ish shell written from scratch, with no dependencies.

Turning an input line into arguments is split in two layers:

1. `classify_character` is pure. Given one character and the current lexer
   state, it decides what that character means and returns the state that
   follows it. It owns no buffer and appends to nothing.
2. `tokenizer` owns the mutable side: the buffer of the token being built and
   the list of finished tokens. It only applies the verdicts it receives.

Keeping the decision stateless is what keeps the quoting rules readable —
each rule is a single branch of one function instead of a flag read from
three places.
"""

# TODO: move the lexer (Verdict, Result, Tokenizer_State, classify_character,
# tokenizer) into its own module and keep main.py for the REPL + builtins

import os
import sys
import subprocess
from enum import Enum
from typing import NamedTuple

built_ins = {"exit", "type", "echo", "pwd", "cd"}

DOUBLE_QUOTE_ESCAPABLE = {"$", "`", '"', "\\", "\n"}


class Verdict(Enum):
    """What the tokenizer should do with the current character"""

    ACCUMULATE = "accumulate"  # append Result.text to the current buffer
    FLUSH = "flush"  # the token ends here; emit the buffer
    SKIP = "skip"  # syntax only (a quote or a backslash); emit nothing


class Result(NamedTuple):
    """A verdict for one character, plus the lexer state that follows it.

    `text` is what should be accumulated: usually the character itself, but a
    backslash that is not escapable inside double quotes keeps both characters.
    """

    verdict: Verdict
    quote_type: str | None = None
    escaping: bool = False
    text: str = ""


class Tokenizer_State(NamedTuple):
    """Everything needed to resume tokenizing on the next input line.

    buffer: characters of the token currently being built
    saw_quote: a quote was opened while building this token, so it must be
        emitted even when empty (`echo ""` yields one empty argument)
    quote_type: None outside quotes, otherwise the opening quote character
    escaping: the previous character was a backslash that escapes this one
    tokens: the tokens already finished
    unfinished: the line ended mid-escape, so the caller must read one more
    """

    buffer: list[str] | None = None
    saw_quote: bool = False
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
    """Return the action, the text to emit, and the updated state.

    The rules, in the order they are checked:

    - escaping: the character is literal. Inside double quotes only the
      characters in DOUBLE_QUOTE_ESCAPABLE can be escaped, so any other one
      keeps the backslash that preceded it.
    - a backslash outside single quotes: consumed, and turns escaping on.
    - a quote: opens, closes, or — when it is the other kind — is literal.
    - an unquoted space: ends the current token.
    - anything else: literal.
    """

    # This only runs on the character right after a backslash
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
    """Split one input line into tokens, resuming from `state`.

    A fresh Tokenizer_State() starts a new command. Feeding the returned state
    back in continues a line that ended on a trailing backslash, which is how
    line continuation works: the buffer survives across calls.
    """

    quote_type = state.quote_type
    escaping = state.escaping
    buffer = state.buffer or []  # If state.buffer is None, the buffer resets
    tokens = state.tokens or []  # Same here but for Tokens
    saw_quote = state.saw_quote

    for char in command:
        verdict, quote_type, escaping, text = classify_character(
            char, quote_type, escaping
        )

        # Being inside quotes marks the token as quoted, so `""` still emits one
        if quote_type:
            saw_quote = True

        if verdict is Verdict.SKIP:
            continue

        elif verdict is Verdict.ACCUMULATE:
            buffer.append(text)

        else:
            # FLUSH: an empty quoted token counts, a run of spaces does not
            if buffer or saw_quote:
                tokens.append("".join(buffer))
                buffer = []
                saw_quote = False
            continue

    # The line ended on a backslash: keep the buffer and ask for another line
    if escaping:
        return Tokenizer_State(
            buffer=buffer,
            tokens=tokens,
            quote_type=quote_type,
            escaping=escaping,
            saw_quote=saw_quote,
            unfinished=True,
        )

    # End of line closes the last token
    if buffer or saw_quote:
        tokens.append("".join(buffer))

    return Tokenizer_State(
        buffer=buffer,
        tokens=tokens,
        quote_type=quote_type,
        escaping=escaping,
        unfinished=False,
    )


def main():
    """The REPL: read a line, tokenize it, dispatch to a builtin or to PATH."""

    while True:
        # TODO: extract line reading into receive_command() to drop the nested whiles
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
