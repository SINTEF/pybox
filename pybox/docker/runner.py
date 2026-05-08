import sys
import json
import traceback

def main():
    stdin = sys.stdin.read()
    try:
        payload = json.loads(stdin)
    except Exception as e:
        print(f"Invalid JSON input: {e}:\n{stdin!r}", file=sys.stderr)
        sys.exit(1)

    code = payload.get("code", "")
    user_input = payload.get("input", {})

    ns = user_input.copy()
    ns["result"] = None
    try:
        exec(code, None, ns)
        sys.stdout.write(json.dumps({"result": ns["result"]}))
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
