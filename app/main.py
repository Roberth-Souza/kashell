import os
import sys

built_ins = set({"exit", "type", "echo"})

def check_path(cmd_name: str) -> str | None:

    path_env = os.environ.get("PATH", "")
    for dir in path_env.split(os.pathsep):
        full_path = os.path.join(dir, cmd_name)

        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path

    return None

def main():
    while True:
        _ = sys.stdout.write("$ ")
        command = input()

        if command.startswith("echo "):
            print(command[5:])

        elif command.startswith("type "):
            cmd_name = command.split()[1]

            if cmd_name in built_ins:
                print(f"{cmd_name} is a shell builtin")

            else:
                find = check_path(cmd_name)
                if find is not None:
                    print(f"{cmd_name} is {find}")
                else:
                    print(f"{cmd_name}: not found")


        elif command == "exit":
            break

        else:
            print(f"{command}: command not found")
            continue


if __name__ == "__main__":
    main()
