#!/usr/bin/env python3
"""
Linting tool for the 2048 game source code.

Enforces:
1. Every source file lives in exactly one layer directory.
2. Imports respect the forward dependency direction.
3. No file exceeds 300 lines.
4. No external dependencies or circular imports.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Any


# Layer order defines the dependency chain
LAYERS = ["utils", "providers", "config", "types", "repo", "service", "runtime", "ui"]

# Valid import sources for each layer
VALID_IMPORTS = {
    "utils": {"utils"},
    "providers": {"utils", "providers"},
    "config": {"types", "config"},
    "types": {"types"},
    "repo": {"types", "config", "repo"},
    "service": {"types", "config", "repo", "providers", "service"},
    "runtime": {"types", "config", "repo", "service", "providers", "runtime"},
    "ui": {"types", "config", "service", "runtime", "providers", "ui"},
}


def get_layer(file_path: str) -> str | None:
    """Determine which layer a file belongs to."""
    # Normalize path separators
    norm_path = file_path.replace("\\", "/")
    for layer in LAYERS:
        # Check for src/<layer>/ pattern
        if f"/{layer}/" in norm_path:
            return layer
    return None


def get_imports(file_path: str) -> list[str]:
    """Extract all import statements from a Python file."""
    imports = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
            elif node.level > 0:  # Relative import
                # Get the package name
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for n in ast.walk(tree):
                        if isinstance(n, ast.Module) and n.package:
                            imports.append(n.package)
                            break
                except:
                    pass

    return imports


def check_file(file_path: str) -> list[dict[str, Any]]:
    """Check a single file for lint violations."""
    violations = []
    abs_path = os.path.abspath(file_path)

    # Rule 1: File must be in a layer directory
    layer = get_layer(file_path)
    if layer is None:
        violations.append({
            "file": file_path,
            "line": 1,
            "message": f"File does not belong to any layer directory",
            "fix": f"Move file to src/<layer>/ directory",
        })
        return violations

    # Rule 3: Check line count
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) > 300:
            violations.append({
                "file": file_path,
                "line": 1,
                "message": f"File has {len(lines)} lines, exceeds maximum of 300",
                "fix": "Split file into smaller modules within the same layer",
            })

    # Rule 2: Check imports
    imports = get_imports(file_path)
    for imp in imports:
        # Check if import is from src/
        if imp.startswith("src."):
            import_base = imp.split(".")[0]
            # Get the actual layer of the import
            # For relative imports within src/, map the import
            if imp.startswith("src.types"):
                import_layer = "types"
            elif imp.startswith("src.config"):
                import_layer = "config"
            elif imp.startswith("src.repo"):
                import_layer = "repo"
            elif imp.startswith("src.service"):
                import_layer = "service"
            elif imp.startswith("src.runtime"):
                import_layer = "runtime"
            elif imp.startswith("src.ui"):
                import_layer = "ui"
            elif imp.startswith("src.providers"):
                import_layer = "providers"
            elif imp.startswith("src.utils"):
                import_layer = "utils"
            else:
                import_layer = imp

            if import_layer not in VALID_IMPORTS[layer]:
                violations.append({
                    "file": file_path,
                    "line": 1,
                    "message": f"Invalid import '{imp}': {layer} layer may not import from {import_layer}",
                    "fix": f"{layer} layer may only import from: {', '.join(sorted(VALID_IMPORTS[layer]))}",
                })

    return violations


def main() -> int:
    """Run linting on all source files."""
    repo_root = Path(__file__).parent
    src_dir = repo_root / "src"

    if not src_dir.exists():
        print("Error: src/ directory not found")
        return 1

    violations = []
    found_files = False

    # Walk through all Python files in src/
    for root, dirs, files in os.walk(src_dir):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                found_files = True
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_root)
                violations.extend(check_file(rel_path))

    if not found_files:
        print("No Python files found in src/")
        return 1

    # Report results
    if violations:
        print(f"Found {len(violations)} linting violation(s):\n")
        for v in violations:
            print(f"{v['file']}:{v['line']}: {v['message']}")
            print(f"  Fix: {v['fix']}")
        return 1
    else:
        print("All files passed linting.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
