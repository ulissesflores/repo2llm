#!/usr/bin/env python3
"""
repo2llm - Project Context Generator

This module traverses a directory structure and generates a single text output
containing the file tree and file contents, optimized for Large Language Model
(LLM) context windows. It respects a custom .llmignore configuration file.

Author: Ulisses Flores
License: Apache-2.0
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Set, Optional, Union

# --- Constants & Defaults ---

DEFAULT_IGNORE_DIRS: Set[str] = {
    '.git', 'node_modules', '__pycache__', 'venv', '.venv', 'env', 
    '.idea', '.vscode', 'runs', 'dist', 'build', 'coverage', 
    '.pytest_cache', '.mypy_cache', 'tmp', 'temp', 'obj', 'bin'
}

DEFAULT_IGNORE_FILES: Set[str] = {
    '.DS_Store', 'Thumbs.db', 'package-lock.json', 'yarn.lock', 
    'pnpm-lock.yaml', 'poetry.lock', 'Gemfile.lock'
}

DEFAULT_IGNORE_EXT: Set[str] = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', 
    '.exe', '.bin', '.dll', '.so', '.dylib', '.class', '.jar',
    '.zip', '.tar', '.gz', '.pdf', '.pyc', '.pyo', 
    '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.mp3'
}

TRUNCATE_EXT: Set[str] = {
    '.csv', '.log', '.tsv', '.jsonl', '.sql'
}

MAX_TRUNCATE_LINES: int = 10


class ContextGenerator:
    """
    Handles the traversal and processing of project files to generate 
    a consolidated text representation.
    """

    def __init__(self, root_dir: Path, output_path: Optional[Path] = None):
        """
        Initialize the generator with a root directory.

        Args:
            root_dir (Path): The root directory of the project to scan.
            output_path (Path, optional): Absolute path to the output file when stdout is redirected.
                When provided and the file is within the scanned root, it will be excluded to prevent
                self-inclusion and unbounded growth.
        """
        self.root: Path = root_dir.resolve()
        self.ignore_dirs: Set[str] = DEFAULT_IGNORE_DIRS.copy()
        self.ignore_files: Set[str] = DEFAULT_IGNORE_FILES.copy()
        self.ignore_ext: Set[str] = DEFAULT_IGNORE_EXT.copy()
        
        # When output is redirected to a file inside the scanned root, exclude it to prevent
        # self-inclusion (e.g., `... > relatorio.txt`) and exponential growth across runs.
        self.output_path: Optional[Path] = output_path.resolve() if output_path else None

        self._load_config()

    def _load_config(self) -> None:
        """
        Loads configuration from a .llmignore file in the project root, if it exists.
        
        The .llmignore format supports:
        - `name/` to ignore directories.
        - `*.ext` to ignore extensions.
        - `filename` to ignore specific files.
        """
        config_path = self.root / '.llmignore'
        if not config_path.exists():
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.endswith('/'):
                        self.ignore_dirs.add(line[:-1])
                    elif line.startswith('*.'):
                        self.ignore_ext.add(line[1:])
                    else:
                        self.ignore_files.add(line)
        except PermissionError:
            sys.stderr.write(f"Warning: Permission denied reading {config_path}\n")

    def should_ignore(self, path: Path) -> bool:
        """
        Determines if a given path should be ignored based on the configuration.

        Args:
            path (Path): The path to check.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        name = path.name

        # Safety: if stdout is redirected to a file that lives inside the target root, do not
        # include that file in the scan/output (prevents self-inclusion).
        if self.output_path:
            try:
                resolved = path.resolve()
            except OSError:
                return True

            if resolved == self.output_path:
                return True

            # If the output file is inside the scanned root, also exclude it even if reached
            # via relative/alternate paths.
            try:
                resolved.relative_to(self.root)
                self.output_path.relative_to(self.root)
            except ValueError:
                pass
            else:
                if resolved == self.output_path:
                    return True

        # Always verify if the path exists to avoid errors on broken symlinks
        if not path.exists():
            return True

        if path.is_dir():
            # Check for exact directory match or hidden directories (excluding .git/ intentionally if needed)
            if name in self.ignore_dirs:
                return True
            if name.startswith('.') and name != '.git': # git is handled in ignore_dirs usually
                return True
            return False
        
        if path.is_file():
            # Never ignore the config file itself if it appears in the list
            if name in {'.llmignore', '.llmignore.example'}:
                return False
                
            if name in self.ignore_files:
                return True
            if name.startswith('.'):
                return True
            if path.suffix.lower() in self.ignore_ext:
                return True
            
        return False

    def generate_tree(self, directory: Optional[Path] = None, prefix: str = "") -> None:
        """
        Prints the directory tree structure visually to stdout.

        Args:
            directory (Path, optional): The directory to print. Defaults to self.root.
            prefix (str): The prefix string for the current line (recursion indentation).
        """
        target_dir = directory or self.root
        
        try:
            # Sort directories first, then files, case-insensitive
            children = sorted(
                target_dir.iterdir(), 
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
        except PermissionError:
            print(f"{prefix}[ACCESS DENIED]")
            return

        # Filter out ignored paths
        filtered_children = [c for c in children if not self.should_ignore(c)]
        count = len(filtered_children)

        for i, path in enumerate(filtered_children):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{path.name}")

            if path.is_dir():
                extension = "    " if is_last else "│   "
                self.generate_tree(path, prefix + extension)

    def dump_contents(self) -> None:
        """
        Iterates through the project files and prints their contents to stdout.
        Handles truncation for large/log files and skips binaries.
        """
        for root, dirs, files in os.walk(self.root):
            root_path = Path(root)
            
            # Prune directories in-place to prevent walking into ignored folders
            dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d)]
            dirs.sort() # Ensure deterministic order

            for file_name in sorted(files):
                file_path = root_path / file_name
                
                if self.should_ignore(file_path):
                    continue

                self._print_file_content(file_path)

    def _print_file_content(self, file_path: Path) -> None:
        """
        Helper method to print a single file's content with formatting.
        """
        try:
            rel_path = file_path.relative_to(self.root)
        except ValueError:
            rel_path = file_path

        header_bar = "=" * 80
        print(f"\n{header_bar}")
        print(f"FILE: {rel_path}")
        print(f"{header_bar}\n")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                # Handle truncation for large data/log files
                if file_path.suffix.lower() in TRUNCATE_EXT:
                    print(f"[NOTE: File truncated to first {MAX_TRUNCATE_LINES} lines]\n")
                    for _ in range(MAX_TRUNCATE_LINES):
                        line = f.readline()
                        if not line:
                            break
                        print(line, end='')
                    print("\n... [REMAINING CONTENT HIDDEN] ...")
                else:
                    # Check for binary content via simple heuristic
                    content = f.read()
                    if '\0' in content:
                        print("[BINARY CONTENT DETECTED - SKIPPED]")
                    else:
                        print(content)
                        
        except Exception as e:
            print(f"[ERROR READING FILE: {e}]")


def main() -> None:
    """
    CLI Entry point.
    """
    parser = argparse.ArgumentParser(
        description="Generate a text snapshot of a project for LLM context."
    )
    parser.add_argument(
        "path", 
        nargs="?", 
        default=".", 
        help="Path to the target project directory (default: current dir)"
    )
    
    args = parser.parse_args()
    target_path = Path(args.path).resolve()

    if not target_path.exists() or not target_path.is_dir():
        sys.stderr.write(f"Error: The directory '{target_path}' does not exist.\n")
        sys.exit(1)

    output_path: Optional[Path] = None

    # If stdout is redirected (e.g., `> relatorio.txt`), attempt to detect the target file so we can
    # exclude it from the scan. This prevents the output file from being included in itself.
    if not sys.stdout.isatty():
        try:
            # `sys.stdout.name` is typically the path when redirected to a file.
            output_path = Path(os.path.realpath(getattr(sys.stdout, 'name', '')))
        except Exception:
            output_path = None

    generator = ContextGenerator(target_path, output_path=output_path)

    print("PROJECT STRUCTURE:")
    print("==================")
    print(f"Root: {target_path.name}")
    generator.generate_tree()
    
    print("\n\nPROJECT FILE CONTENTS:")
    generator.dump_contents()


if __name__ == "__main__":
    main()