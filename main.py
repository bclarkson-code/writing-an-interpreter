import getpass
from argparse import ArgumentParser
from pathlib import Path

from writing_an_interpreter import repl
from writing_an_interpreter.environment import Environment


def run_repl():
    user = getpass.getuser()
    print(f"Hello {user}! This is the Monkey programming language!")
    print("Feel free to type in commands")
    repl.start()


def execute_file(path: Path):
    contents = path.read_text()
    environment = Environment()
    environment = repl.load_standard_library(environment)
    repl.execute_string(contents, environment)


if __name__ == "__main__":
    argparse = ArgumentParser()
    argparse.add_argument(
        "path", nargs="?", help="Path of the file to be exeucted", default=""
    )

    args = argparse.parse_args()

    if args.path:
        execute_file(Path(args.path))
    else:
        run_repl()
