"""Auto completitions for my shell :)"""

import readline

from app.handlers import built_ins


def completer(text: str, state: int) -> str | None:
    matches = [command for command in built_ins if command.startswith(text)]
    return matches[state] + " " if state < len(matches) else None


readline.set_completer(completer)
readline.parse_and_bind("tab: complete")
