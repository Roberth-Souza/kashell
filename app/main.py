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


def check_in_builtins(args: str) -> bool:
    return args in built_ins


def handle_type(args: str) -> str:

    if check_in_builtins(args):
        return f"{args} is a shell builtin"

    else:
        find = find_executable(args)
        if find is not None:
            return f"{args} is {find}"
        return f"{args}: not found"


def current_directory() -> str:
    return os.getcwd()


def change_directory(path: str):

    if os.path.isdir(path):
        os.chdir(path)
        return

    elif path == "~":
        home = os.path.expanduser("~")
        os.chdir(home)
        return

    raise ValueError(f"cd: {path}: No such file or directory")


def main():

    while True:
        _ = sys.stdout.write("$ ")
        command = input()

        if not command or not command.strip():
            continue

        cmd_split = command.split()
        cmd_name = cmd_split[0]
        args = cmd_split[1:]

        if cmd_name == "echo":
            print(" ".join(args))

        elif cmd_name == "type":
            result = handle_type(args[0])
            print(result)

        elif cmd_name == "pwd":
            print(current_directory())

        elif cmd_name == "cd":
            try:
                change_directory(args[0])
            except ValueError as err:
                print(err)

        elif cmd_name == "exit":
            break

        elif (exec_path := find_executable(cmd_name)) is not None:
            _ = subprocess.run(cmd_split, executable=exec_path)

        else:
            print(f"{command}: command not found")
            continue


if __name__ == "__main__":
    main()
