# Monkey Programming Language Interpreter (Python)

This project is a Python implementation of the Monkey programming language, based on the book "Writing An Interpreter In Go" by Thorsten Ball. The interpreter is written from scratch and demonstrates fundamental concepts of programming language design and implementation.

## About Monkey Language

Monkey is a programming language that supports:

- C-like syntax
- Variable bindings
- Integer and boolean data types
- Arithmetic expressions
- Built-in functions
- First-class and higher-order functions
- Closures
- String data structure
- Array data structure
- Hash data structure

## Features

- **Lexical Analysis**: Transforms source code into tokens
- **Recursive Descent Parser**: Creates an abstract syntax tree (AST) from tokens
- **Tree-Walking Evaluator**: Executes the AST
- **REPL**: Interactive environment for testing Monkey code

## Code Examples

Here's a taste of what Monkey code looks like:

```monkey
// Binding a value to a name
let age = 1;

// Defining a function
let add = fn(a, b) { return a + b; };

// Using arrays
let myArray = [1, 2, 3, 4, 5];

// Using hash maps
let ben = {"name": "Ben", "age": 27};

// Higher order functions
let twice = fn(f, x) {
    return f(f(x));
};

// Closures
let addTwo = fn(x) {
    return x + 2;
};

twice(addTwo, 2); // => 6
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pytest (for running tests)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/bclarkson-code/writing-an-interpreter.git
cd monkey-python
```

2. Install the package in development mode:
```bash
pip install -e .
```

### Running the REPL

To start the interactive REPL:

```bash
python main.py
```

### Running Example Scripts

The project includes example Monkey scripts:

- `example_script.🐵`: Demonstrates basic language features
- `standard_library.🐵`: Contains standard library functions

To run a Monkey script:

```bash
python main.py example_script.🐵
```

### Running Tests

```bash
pytest tests/
```

## Project Structure

```
.
├── README.md
├── example_script.🐵
├── main.py
├── pyproject.toml
├── src/
│   └── writing_an_interpreter/
│       ├── __init__.py
│       ├── ast.py
│       ├── environment.py
│       ├── evaluator.py
│       ├── lexer.py
│       ├── objects.py
│       ├── parser.py
│       ├── repl.py
│       ├── standard_library.🐵
│       └── tokens.py
└── tests/
    ├── test_evaluator.py
    ├── test_lexer.py
    ├── test_objects.py
    └── test_parser.py
```

## Implementation Details

This interpreter follows these main steps:

1. **Lexical Analysis**: The lexer breaks down the source code into tokens
2. **Parsing**: The parser creates an Abstract Syntax Tree (AST) from these tokens
3. **Evaluation**: The evaluator walks through the AST and executes the code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Thorsten Ball for writing the excellent book "Writing An Interpreter In Go"
- The original Monkey language specification

## License

This project is licensed under the MIT License - see the LICENSE file for details.
