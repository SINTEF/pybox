import sys
import json
import traceback


def main():
    """Entry point for executing user-provided code inside a sandbox.

    This function:
    1. Reads a JSON payload from stdin.
    2. Extracts the Python code and input variables.
    3. Executes the code in a controlled namespace.
    4. Writes the result to stdout as JSON.

    The input JSON is expected to have the following structure:
        {
            "code": "<python code as string>",
            "input": { ... arbitrary key-value pairs ... }
        }

    The executed code is expected to assign its output to a variable
    named `result`.

    Behavior:
        - On successful execution, writes:
            {"result": <value>}
          to stdout.
        - On invalid JSON input, prints an error to stderr and exits with code 1.
        - On execution error, prints the traceback to stderr and exits with code 1.

    Notes:
        - The execution namespace is initialized with the provided input data.
        - The namespace is mutable; user code can overwrite variables.
        - No validation or sandboxing is performed here; isolation must be
          enforced externally (e.g., via Docker, seccomp, etc.).
    """
    stdin = sys.stdin.read()

    try:
        payload = json.loads(stdin)
    except Exception as e:
        print(f"Invalid JSON input: {e}:\n{stdin!r}", file=sys.stderr)
        sys.exit(1)

    code = payload.get("code", "")
    user_input = payload.get("input", {})

    # Prepare execution namespace
    ns = user_input.copy()
    ns["result"] = None

    try:
        exec(code, None, ns)
        sys.stdout.write(json.dumps({"result": ns["result"]}))
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    """Run the executor when invoked as a script."""
    main()
