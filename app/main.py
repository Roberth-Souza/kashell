import sys

built_ins = set({"exit", "type", "echo"})


def main():
    while True:
        _ = sys.stdout.write("$ ")
        command = input()

        if command.startswith("echo "):
            print(command[5:])

        elif command.startswith("type "):
            if command[5:] in built_ins:
                print(f"{command.split()[1]} is a shell builtin")
            else:
                print(f"{command.split()[1]}: not found")

        elif command == "exit":
            break

        else:
            print(f"{command}: command not found")
            continue


if __name__ == "__main__":
    main()
