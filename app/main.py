import sys


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()

        if command.split()[0] == "echo":
            print(command[5:])

        elif command == "exit":
            break

        else:
            print(f"{command}: command not found")
            continue


if __name__ == "__main__":
    main()
