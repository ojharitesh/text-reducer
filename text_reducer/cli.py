"""Command-line interface for text-reducer."""

import argparse
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from .reducer import InputDoesNotFail, reduce_text


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minimize a text file while preserving a checker failure."
    )
    parser.add_argument("input", type=Path, help="input text file")
    parser.add_argument(
        "--command",
        required=True,
        help="checker command; use {} for the candidate file path",
    )
    return parser.parse_args()


def _command_args(command: str, candidate: Path) -> list[str]:
    if "{}" not in command:
        raise ValueError("checker command must contain {}")
    try:
        parts = shlex.split(command)
    except ValueError as error:
        raise ValueError(f"invalid checker command: {error}") from error
    if not parts:
        raise ValueError("checker command cannot be empty")
    # Split arguments without invoking a shell, then substitute the candidate path.
    return [part.replace("{}", str(candidate)) for part in parts]


def main() -> int:
    args = _arguments()
    try:
        with args.input.open("r", encoding="utf-8", newline="") as input_file:
            original = input_file.read()
    except OSError as error:
        print(f"error: cannot read input file: {error}", file=sys.stderr)
        return 2

    try:
        with tempfile.TemporaryDirectory() as directory:
            candidate_path = Path(directory) / "candidate.txt"

            def checker(candidate: str) -> bool:
                try:
                    # Reuse one temporary path for each candidate tested by the reducer.
                    with candidate_path.open(
                        "w", encoding="utf-8", newline=""
                    ) as candidate_file:
                        candidate_file.write(candidate)
                    completed = subprocess.run(
                        _command_args(args.command, candidate_path),
                        check=False,
                        capture_output=True,
                    )
                except (OSError, ValueError) as error:
                    raise RuntimeError(f"cannot run checker: {error}") from error
                # The reducer treats any nonzero checker status as a failure.
                return completed.returncode != 0

            result = reduce_text(original, checker)
    except InputDoesNotFail as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"Original length: {len(original)}")
    print(f"Reduced length: {len(result.text)}")
    print(f"Tests: {result.tests}")
    print("Reduced input:")
    print(result.text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
