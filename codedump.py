#!/usr/bin/env python3
"""
codedump.py  –  Concatenate or split source files, with options:

  -l / --list-only   Only list file paths
  -s / --split       Write each file (with header) to its own text file
  -F / --flatten     (with --split) put all output files in one folder
  --output-dir DIR   Destination for split or dump file (default: extracted/)

NEW IN THIS VERSION
───────────────────────────────────────────────────────────────────────────────
• Binary-file sniffing:  any file whose first 4 KB contains a NUL (0x00) byte
  is treated as binary and skipped (reported in output).
• Residual “\x00” chars are stripped from all text reads.
"""

# ─── Imports ──────────────────────────────────────────────────────────────────
import os
import re
import sys
import argparse
import datetime
import pyperclip
from collections import defaultdict

# ─── General helpers ──────────────────────────────────────────────────────────
def get_file_info(file_path):
    """Return size and mtime (as yyyy-mm-dd HH:MM:SS) for *file_path*."""
    try:
        s = os.stat(file_path)
        return {
            "size": s.st_size,
            "last_modified": datetime.datetime.fromtimestamp(s.st_mtime)
            .strftime("%Y-%m-%d %H:%M:%S"),
        }
    except FileNotFoundError:
        return {"size": "N/A", "last_modified": "N/A"}


# ─── Binary / NUL-clean helpers ───────────────────────────────────────────────
def _looks_binary(path, sniff=4096):
    """
    Very quick heuristic: read up to *sniff* bytes and
    return True if a NUL byte is present → likely binary.
    """
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(sniff)
        return b"\x00" in chunk
    except Exception:
        return False  # On I/O problems treat as text – caller will handle.


def _read_text(path):
    """
    Read *path* as text; remove any 0x00 bytes.

    • Try UTF-8 first; on failure fall back to latin-1 (ignore errors).
    • Strip all NUL characters so they never reach the output/log/clipboard.
    """
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError:
            txt = raw.decode("latin-1", "ignore")
        return txt.replace("\x00", "")
    except Exception as exc:
        return f"[ERROR reading file: {exc}]"


# ─── Skip-logic (unchanged from earlier) ──────────────────────────────────────
def should_skip(path):
    """Return True if *path* (file or dir) should be excluded."""
    # — Allowed extensions / filenames / skip lists (same as previous version) —
    allowed_extensions = {
        # General text / data
        ".txt", ".md", ".markdown", ".json", ".xml", ".yaml", ".yml", ".toml",
        ".ini", ".cfg", ".conf", ".sql", ".graphql", ".proto",
        # Python
        ".py", ".pyx", ".pyd", ".pyo", ".pyc", ".pyw", ".pyi",
        # C / C++
        ".c", ".h", ".i", ".cpp", ".hpp", ".cc", ".hh", ".cxx", ".hxx",
        # Julia
        ".jl",
        # JavaScript / TypeScript
        ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
        # Web
        ".html", ".htm", ".css", ".scss", ".sass", ".less",
        # Java & JVM
        ".java", ".kt", ".kts", ".groovy", ".scala", ".clj", ".cljs",
        # .NET
        ".cs", ".fs", ".vb",
        # Ruby
        ".rb", ".rake", ".gemspec",
        # PHP
        ".php", ".phtml", ".php3", ".php4", ".php5", ".phps",
        # Go
        ".go",
        # Rust
        ".rs",
        # Swift
        ".swift",
        # Shell
        ".sh", ".bash", ".zsh", ".fish",
        # PowerShell
        ".ps1", ".psm1", ".psd1",
        # Perl
        ".pl", ".pm",
        # Lua
        ".lua",
        # Haskell
        ".hs", ".lhs",
        # R
        ".r", ".R", ".Rmd",
        # Dart
        ".dart",
        # Kotlin
        ".kt", ".kts",
        # Objective-C
        ".m", ".mm",
        # Elm
        ".elm",
        # F#
        ".fs", ".fsi", ".fsx",
        # Elixir
        ".ex", ".exs",
        # Erlang
        ".erl", ".hrl",
        # Lisp
        ".lisp", ".cl", ".el",
        # Fortran
        ".f", ".for", ".f90", ".f95", ".f03", ".f08",
        # MATLAB / Octave
        ".m", ".mat",
        # Scala
        ".scala", ".sc",
        # Terraform
        ".tf", ".tfvars",
        # LaTeX
        ".tex", ".sty", ".cls",
    }

    allowed_filenames = {
        "readme", "license", "dockerfile", "makefile", ".gitignore",
        ".dockerignore", ".editorconfig", ".env", "requirements.txt",
        "package.json", "tsconfig.json",
        "setup.py", "setup.cfg", "pyproject.toml", "pipfile", "manifest.in",
        ".pylintrc", ".flake8", "pytest.ini", "tox.ini",
        "cmakelist.txt", "cmakelists.txt",
        "project.toml", "manifest.toml", "juliaconfig.toml",
        ".npmignore", ".babelrc", ".eslintrc", ".prettierrc", "tslint.json",
        "webpack.config.js", "yarn.lock",
        "gemfile", "rakefile",
        "composer.json", "composer.lock",
        "go.mod", "go.sum",
        "cargo.toml", "cargo.lock",
        "packages.config", "nuget.config",
        "pom.xml", "build.gradle", "build.gradle.kts",
        "settings.gradle", "settings.gradle.kts",
        "docker-compose.yml", "docker-compose.yaml",
        ".gitattributes",
        ".travis.yml", ".gitlab-ci.yml", "jenkins.file", "azure-pipelines.yml",
        ".vscode", ".idea",
        "elm.json",
        "paket.dependencies", "paket.lock",
        "mix.exs", "mix.lock",
        "rebar.config",
        ".octaverc",
        "build.sbt",
        ".terraform.lock.hcl",
        "ansible.cfg", "hosts",
        "latexmkrc",
    }

    skip_directories = {
        "__pycache__", "node_modules", "venv", "env", ".venv", ".env",
        "build", "dist", "target", "out", "bin", "obj",
        ".git", ".svn", ".hg",
        ".idea", ".vscode",
        "logs", "output",
        ".next",
    }

    skip_filenames = {"package-lock.json"}

    skip_dir_patterns = [r"\.egg-info$"]
    skip_file_patterns = [
        r"\.log(\.[0-9]+)?$", r"^log\.", r"\.bak$", r"\.tmp$",
        r"\.temp$", r"\.swp$", r"~$",
    ]

    # Fast dir-level check
    try:
        if set(os.path.normpath(path).split(os.sep)) & skip_directories:
            return True
    except Exception:
        pass

    name = os.path.basename(path)
    name_lower = name.lower()
    _, ext = os.path.splitext(name)

    if os.path.isdir(path):
        return any(re.search(p, name) for p in skip_dir_patterns)

    if name_lower in skip_filenames:
        return True
    if any(re.search(p, name_lower) for p in skip_file_patterns):
        return True

    return (
        (name.startswith(".") and name_lower not in allowed_filenames)
        or (ext.lower() not in allowed_extensions
            and name_lower not in allowed_filenames)
    )


# ─── Core operations ──────────────────────────────────────────────────────────
def concatenate_files(directory=".", list_only=False):
    """Return concatenation (or listing) of all relevant files."""
    output = []
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
        for file in files:
            fp = os.path.join(root, file)
            if should_skip(fp):
                continue

            info = get_file_info(fp)

            if list_only:
                output.append(fp)
            else:
                output.append("\n" + "=" * 80)
                output.append(f"File: {fp}")
                output.append(f"Size: {info['size']} bytes")
                output.append(f"Last Modified: {info['last_modified']}")
                output.append("=" * 80 + "\n")

                if _looks_binary(fp):
                    output.append("[binary file skipped]\n")
                else:
                    output.append(_read_text(fp))

    return "\n".join(output)


def split_files(directory=".", output_dir="extracted", *, flatten=False):
    """
    Write each relevant file into its own annotated file.

    • If *flatten* is True, every file goes directly in *output_dir*.
      Duplicate basenames receive suffixes _1, _2, …
    """
    dup_counter: defaultdict[str, int] = defaultdict(int)

    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
        for file in files:
            src = os.path.join(root, file)
            if should_skip(src):
                continue

            info = get_file_info(src)
            header = (
                f"{'='*80}\n"
                f"File: {src}\n"
                f"Size: {info['size']} bytes\n"
                f"Last Modified: {info['last_modified']}\n"
                f"{'='*80}\n\n"
            )

            if _looks_binary(src):
                body = "[binary file skipped]\n"
            else:
                body = _read_text(src)

            annotated = header + body

            # Determine destination
            if flatten:
                base = os.path.basename(src)
                n = dup_counter[base]
                dup_counter[base] += 1
                if n:
                    stem, ext = os.path.splitext(base)
                    base = f"{stem}_{n}{ext}"
                dest = os.path.join(output_dir, base)
            else:
                rel = os.path.relpath(src, directory)
                dest = os.path.join(output_dir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)

            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as out_f:
                out_f.write(annotated)

    print(f"\nAll files have been split into '{output_dir}/'.")


# ─── CLI entrypoint ───────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="Concatenate or split files in a directory."
    )
    p.add_argument("directory", nargs="?", default=".",
                   help="Directory to process (default: current dir)")
    p.add_argument("-l", "--list-only", action="store_true",
                   help="List file paths only")
    p.add_argument("-s", "--split", action="store_true",
                   help="Split each file into its own annotated file")
    p.add_argument(
        "-F", "--flatten", action="store_true",
        help="(with --split) write all output files directly in output dir"
    )
    p.add_argument(
        "--output-dir", default="extracted",
        help="Destination for split files or dump txt (default: extracted/)"
    )

    args = p.parse_args()

    if args.split:
        split_files(args.directory, args.output_dir, flatten=args.flatten)
    else:
        result = concatenate_files(args.directory, args.list_only)
        print(result)
        try:
            pyperclip.copy(result)
            print(f"\nOutput copied to clipboard.")
        except pyperclip.PyperclipException:
            pass


if __name__ == "__main__":
    main()
