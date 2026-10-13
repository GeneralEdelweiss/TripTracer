"""Check active root hierarchy and project-wide reference uniqueness (no libraries)."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def parse(path):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]', path.read_text(encoding="utf-8"))
    stack, roots = [], []
    for token in tokens:
        if token == "(":
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
        elif token == ")":
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if stack or len(roots) != 1:
        raise ValueError(f"Malformed schematic: {path}")
    return roots[0]


def children(node, kind):
    return [item for item in node if isinstance(item, list) and item and item[0] == kind]


def check(root):
    refs = defaultdict(list)
    pages, errors = [], []

    def visit(path, ancestors):
        if path in ancestors:
            errors.append(f"Hierarchy cycle: {path}")
            return
        if not path.is_file():
            errors.append(f"Missing sheet: {path}")
            return
        pages.append(str(path))
        data = parse(path)
        for symbol in children(data, "symbol"):
            props = {p[1]: p[2] for p in children(symbol, "property")}
            ref = props.get("Reference", "")
            refs[ref].append(str(path))
            if not ref or ref.endswith("?"):
                errors.append(f"Unannotated symbol: {path} {ref}")
        for sheet in children(data, "sheet"):
            props = {p[1]: p[2] for p in children(sheet, "property")}
            filename = props.get("Sheetfile")
            if filename:
                visit((path.parent / filename).resolve(), ancestors + [path])
            else:
                errors.append(f"Missing Sheetfile: {path}")

    visit(root.resolve(), [])
    for ref, paths in refs.items():
        if len(paths) > 1:
            errors.append(f"Duplicate reference {ref}: {paths}")
    return {"pages": pages, "symbol_instances": sum(map(len, refs.values())), "errors": errors}


if __name__ == "__main__":
    result = check(Path(sys.argv[1]))
    print(json.dumps(result, indent=2))
    sys.exit(bool(result["errors"]))
