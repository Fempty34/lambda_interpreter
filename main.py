import argparse
import sys
from src.lambda_calc.parser import parse
from src.lambda_calc.evaluator import expand_macroses, reduce_term


def run():
    parser = argparse.ArgumentParser(description="Lambda Calculus Evaluator")
    parser.add_argument("file", help="Path to the source file")
    parser.add_argument("--steps", type=int, default=1000, help="Step limit")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    try:
        program = parse(code)
    except Exception as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    try:
        current_term = expand_macroses(program.target, program.macros)
    except Exception as e:
        print(f"Macro expansion error: {e}")
        sys.exit(1)

    print("Evaluation Started")
    if args.verbose:
        print(f"Step 0: {current_term}")

    step = 0
    while step < args.steps:
        next_term = reduce_term(current_term)

        if next_term is None:
            print("\nResult (Normal Form)")
            print(current_term)
            sys.exit(0)

        current_term = next_term
        step += 1

        if args.verbose:
            print(f"Step {step}: {current_term}")

    print(f"\nTerminated")
    print(f"Limit of {args.steps} steps exceeded.")
    print(f"Last term: {current_term}")


if __name__ == "__main__":
    run()
