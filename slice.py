#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
from typing import List, Optional

# -------- utils

def snake(s: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()

def base_name(expr: ast.expr) -> str:
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        return f"{base_name(expr.value)}.{expr.attr}"
    return ""

def is_testcase_class(node: ast.ClassDef) -> bool:
    return any(base_name(b).endswith("TestCase") for b in node.bases)

def node_src(code: str, node: ast.AST) -> str:
    return ast.get_source_segment(code, node) or ""

# -------- extraction of make_booking

def find_make_booking(tree: ast.Module) -> Optional[ast.FunctionDef]:
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == "make_booking":
            return n
    return None

def ensure_factories_with_make_booking(factories_path: Path, make_booking_src: str) -> None:
    factories_path.parent.mkdir(parents=True, exist_ok=True)
    init_path = factories_path.parent / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")

    if factories_path.exists():
        current = factories_path.read_text(encoding="utf-8")
        if "def make_booking" in current:
            # уже есть — ничего не делаем
            return
        # добавим с разделителем
        new_content = (current.rstrip() + "\n\n" + make_booking_src.rstrip() + "\n")
        factories_path.write_text(new_content, encoding="utf-8")
    else:
        factories_path.write_text(make_booking_src.rstrip() + "\n", encoding="utf-8")

# -------- prelude collection

def collect_prelude_excluding_make_booking(code: str, tree: ast.Module) -> List[str]:
    parts: List[str] = []
    for n in tree.body:
        # keep future imports
        if isinstance(n, ast.ImportFrom) and n.module == "__future__":
            parts.append(node_src(code, n))
        # other imports
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            if isinstance(n, ast.ImportFrom) and n.module in {"src.bookings.tests.factories"}:
                # не нужен (мы добавим явный импорт make_booking ниже)
                continue
            parts.append(node_src(code, n))
        # skip top-level make_booking
        elif isinstance(n, ast.FunctionDef) and n.name == "make_booking":
            continue
    return [p for p in parts if p.strip()]

# -------- main split

def split_by_class(
    src_file: Path,
    out_dir: Path,
    factories_path: Path = Path("src/bookings/tests/factories.py"),
) -> int:
    code = src_file.read_text(encoding="utf-8")
    tree = ast.parse(code, filename=str(src_file))

    # 1) Extract make_booking if present
    make_fn = find_make_booking(tree)
    if make_fn is not None:
        ensure_factories_with_make_booking(factories_path, node_src(code, make_fn))

    # 2) Build prelude (imports etc.) excluding make_booking
    prelude = collect_prelude_excluding_make_booking(code, tree)

    # 3) Add import for make_booking if it existed
    if make_fn is not None:
        prelude.append("from src.bookings.testing.factories import make_booking")

    out_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and is_testcase_class(node):
            class_src = node_src(code, node).rstrip()
            fname = f"test_{snake(node.name)}.py"
            out_path = out_dir / fname

            parts: List[str] = []
            parts.extend(prelude)
            if prelude:
                parts.append("")
            parts.append(class_src)

            out_path.write_text("\n".join(parts) + "\n", encoding="utf-8")
            generated += 1
    return generated

def main():
    ap = argparse.ArgumentParser(description="Split test module into one file per test class and extract make_booking.")
    ap.add_argument("src", help="Path to the source test file.")
    ap.add_argument("-o", "--out-dir", default="src/bookings/tests/unit",
                    help="Output directory for generated files.")
    ap.add_argument("--factories", default="src/bookings/tests/factories.py",
                    help="Path to factories.py to place make_booking.")
    args = ap.parse_args()

    count = split_by_class(Path(args.src), Path(args.out_dir), Path(args.factories))
    print(f"Generated {count} file(s) in {args.out_dir}")

if __name__ == "__main__":
    main()
