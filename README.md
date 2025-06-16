# CodeDump

## Overview

CodeDump is a utility for quickly exploring the contents of any source‑code directory. It can either:

* **Concatenate** every relevant text file into one annotated dump (handy for rapid reviews, AI prompts, or archiving), or
* **Split** each file into its own annotated copy inside an *extracted* folder.

A lightweight **Tk GUI** is included for non‑command‑line users, and a batch script can bundle everything into a single Windows executable so that end‑users do **not** need to install Python.

---

## Feature Summary

| Capability            | Details                                                                                                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Concatenate           | Combines all allowed files into one document, with 80‑char separators and file metadata headers. Output is displayed in the GUI, copied to the clipboard, **and** written to `code_dump_YYYYMMDD_HHMMSS.txt` inside the chosen output directory. |
| Split                 | Writes each file’s annotated copy under `extracted/` (default) or any directory you choose.                                                                                                                                                      |
| Flatten               | `--flatten` (GUI checkbox “Flatten output”) places every split file directly in the output folder, disambiguating duplicate basenames with `_1`, `_2`, …                                                                                         |
| List‑only             | Quickly show just the relative paths that would be processed.                                                                                                                                                                                    |
| Smart skip logic      | Ignores binary files, build artefacts, dependency folders (`node_modules`, `__pycache__`, `.git`, etc.), and common log/backup extensions.                                                                                                       |
| Binary / NUL safety   | Files whose first 4 KB contain a `\x00` byte are treated as binary and skipped. Any stray `\x00` chars that remain are stripped during read.                                                                                                     |
| Clipboard integration | Concatenate output is automatically copied to the clipboard (falls back gracefully if unavailable).                                                                                                                                              |
| One‑file EXE builder  | `build_codedump.bat` uses PyInstaller to create `CodeDump_vX.Y.Z.exe` (GUI, no console).                                                                                                                                                         |

---

## Quick Start (Python users)

```bash
# 1. Clone or download the project
# 2. Create a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate   # PowerShell / CMD on Windows
# 3. Install runtime dependency
pip install pyperclip

# 4. Run the GUI
python codedump_gui.py

# 5. Or use the CLI
python codedump.py path/to/project --split --flatten --output-dir my_dump
```

> **Note:** The only runtime dependency is `pyperclip` (used for clipboard operations). `tkinter` ships with the standard CPython installer on Windows, macOS and most Linux distros.

---

## GUI Usage

1. **Source Directory** – browse to the folder you want to scan.
2. *(Optional)* enable **List only**, **Split files**, or **Flatten output**.
3. **Output Directory** – set where TXT or split files should go (always active).
4. Click **Run**.

* In *concatenate* mode you will see the dump in the log pane and a file such as `code_dump_20250616_161530.txt` will be saved in the output directory.
* In *split* mode the files appear under `extracted/` (or the directory you set). The GUI log lists progress.

---

## Command‑Line Options

```text
usage: codedump.py [directory] [options]

options:
  -l, --list-only          list file paths only
  -s, --split              write each file to its own annotated copy
  -F, --flatten            (with --split) place all files directly in output dir
      --output-dir DIR     destination for split files or dump txt (default: extracted/)
```

Examples:

```bash
# Concatenate a repo and open the result in VS Code
python codedump.py . > dump.txt && code dump.txt

# Split & flatten into one folder
python codedump.py ../legacy --split -F --output-dir legacy_flat
```

---

## Building a Stand‑Alone Windows Executable

1. Ensure you have a **64‑bit Python 3.10+** and a **virtual environment** called `venv` (any folder name is fine but the batch file assumes `venv`).
2. Activate the venv and install build dependencies:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install pyinstaller pyperclip
```

3. Run the batch script:

```powershell
build_codedump.bat
```

4. When prompted, enter a version like `1.0.0`. On success you’ll find `dist\CodeDump_v1.0.0.exe` – distribute that **single file**.

---

## Development Notes

* **Skip logic** is defined in `should_skip()` (in `codedump.py`). Edit the allowed‑extension and skip lists there if you need to support additional file types.
* Binary detection occurs in `_looks_binary()`; adjust the `sniff` byte count if necessary.
* The GUI is plain Tkinter (`codedump_gui.py`) – easy to extend with additional switches.
* The project is entirely cross‑platform for CLI usage; the EXE build is Windows‑only because it uses PyInstaller’s `--onefile` option.

---

## License

MIT License – see `LICENSE` file for full text.

---

## Acknowledgements

* PyInstaller for bundling.
* Pyperclip for painless clipboard access.
* The Python Standard Library (tkinter, argparse, datetime, etc.).
* smat-dev on Github (the creator of the original project this was forked from)