"""Tokenizer for the shell"""

from enum import Enum
from typing import NamedTuple

DOUBLE_QUOTE_ESCAPABLE = {"$", "`", '"', "\\", "\n"}


class Verdict(Enum):
    """What the tokenizer should do with the current character"""

    ACCUMULATE = "accumulate"
    FLUSH = "flush"  # the token ends here; emit the buffer
    SKIP = "skip"


class Result(NamedTuple):
    """A verdict for one character, plus the lexer state that follows it"""

    verdict: Verdict
    quote_type: str | None = None
    escaping: bool = False

    # The character itself, except when a non-escapable
    # backslash inside double quotes has to keep both characters
    text: str = ""


class Tokenizer_State(NamedTuple):
    """Everything needed to resume tokenizing on the next input line"""

    buffer: list[str] | None = None

    # A quote was opened while building this token, so it is emitted even when
    # empty (`echo ""` yields one empty argument)
    saw_quote: bool = False

    quote_type: str | None = None
    escaping: bool = False
    tokens: list[str] | None = None

    # The line ended mid-escape, so the caller must read one more
    unfinished: bool = False


def classify_character(char: str, quote_type: str | None, escaping: bool) -> Result:
    """Return the action, the text to emit, and the updated state"""

    # This only runs on the character right after a backslash
    if escaping:
        # Inside double quotes only DOUBLE_QUOTE_ESCAPABLE can be escaped, so
        # any other character keeps the backslash that preceded it
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

    # Unquoted space: the only character that ends a token
    elif char == " " and quote_type is None:
        return Result(Verdict.FLUSH, quote_type=quote_type, escaping=False)

    # Anything else is literal text
    return Result(Verdict.ACCUMULATE, quote_type=quote_type, escaping=False, text=char)


def tokenizer(command: str, state: Tokenizer_State) -> Tokenizer_State:
    """Split one input line into tokens, resuming from `state`"""

    # A fresh Tokenizer_State() starts a new command; feeding back the state
    # this function returns continues the previous one
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

    # The line ended on a backslash: keep the buffer and the flags untouched so
    # the next line resumes this same token — this is line continuation
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
