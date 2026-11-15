# text-reducer

`text-reducer` is a small educational command-line tool that minimizes a text
file while keeping a user-provided checker failing. It is inspired by the
Fuzzing Book chapter [Reducing Failure-Inducing Inputs](https://www.fuzzingbook.org/html/Reducer.html).

## How it works

The tool uses **delta debugging**: it splits the input into chunks, removes
one chunk at a time, and keeps a removal only when the checker still fails. It
repeats this process until no further reduction is possible. A smaller failing
input is often easier to inspect and helps identify the cause of a bug.

This is a small educational implementation inspired by the chapter, not a
production-grade reducer.

## Installation

With Python 3.9 or newer:

```sh
python -m pip install .
```

For development, the command can also be run without installing:

```sh
python -m text_reducer.cli failing_input.txt --command "python checker.py {}"
```

## Usage

The command must contain `{}`, which is replaced with the path to a temporary
file containing each candidate input:

```sh
text-reducer failing_input.txt --command "python checker.py {}"
```

For example, save this checker as `checker.py`:

```python
import sys

with open(sys.argv[1], encoding="utf-8") as file:
    sys.exit(1 if "needle" in file.read() else 0)
```

With `failing_input.txt` containing:

```text
some irrelevant text
needle
more irrelevant text
```

the reduced output includes:

```text
needle
```

The checker should return a **nonzero exit code when the failure is present**
and zero when the candidate is accepted. The tool first confirms that the
original input fails. It then prints the original length, reduced length,
number of checker tests, and reduced input.

## Limitations

This tool reduces text without understanding its syntax, so the result may be
syntactically invalid. For structured languages, grammar-based reduction is
usually better. The checker is run as a direct subprocess command (not through
a shell), so shell pipelines and shell operators are not supported.
