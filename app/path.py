"""PATH lookup: locate an executable across the directories in $PATH."""

import os


def find_executable(cmd_name: str) -> str | None:
    """Checks all directories in PATH in search for an executable"""

    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(os.pathsep):
        full_path = os.path.join(directory, cmd_name)

        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path

    return None
