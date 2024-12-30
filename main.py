import getpass

from writing_an_interpreter import repl

if __name__ == "__main__":
    user = getpass.getuser()
    print(f"Hello {user}! This is the Monkey programming language!")
    print("Feel free to type in commands")
    repl.start()
