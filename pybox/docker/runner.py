import sys
import json
import traceback

def main():
    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        print(f"Invalid input JSON: {e}", file=sys.stderr)
        sys.exit(1)

    code = payload.get("code", "")
    user_input = payload.get("input", {})

    globals_ns = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "dict": dict,
            "list": list,
            "set": set,
            "tuple": tuple,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
        }
    }
    locals_ns = {"input_data": user_input, "result": None}

    try:
        exec(code, globals_ns, locals_ns)
        sys.stdout.write(json.dumps({"result": locals_ns["result"]}))
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
