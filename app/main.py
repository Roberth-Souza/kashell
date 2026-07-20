import os
import sys
import subprocess

built_ins = set({"exit", "type", "echo", "pwd", "cd"})


def find_executable(cmd_name: str) -> str | None:
    """Checks all directories in PATH in search for an executable"""

    path_env = os.environ.get("PATH", "")
    for dir in path_env.split(os.pathsep):
        full_path = os.path.join(dir, cmd_name)

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


def tokenizer(command: str) -> list[str]:
    buffer = ""
    result: list[str] = []
    inside_quote = False

    for tokken in command:
        if tokken == "'":  # single quote
            inside_quote = not inside_quote

        elif inside_quote:
            buffer += tokken

        else:
            if tokken == " ":
                if not buffer:
                    continue

                else:
                    result.append(buffer)
                    buffer = ""

            else:
                buffer += tokken

    if not buffer:
        return result

    result.append(buffer)
    return result


def main():

    while True:
        _ = sys.stdout.write("$ ")
        command = input()

        if not command or not command.strip():
            continue

        cmd_split = tokenizer(command)
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
