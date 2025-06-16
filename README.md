# CodeDump

CodeDump is a simple Python CLI tool that scans a directory for code and configuration files and either:

* **Concatenates** them into one annotated output (with size and last-modified metadata), or
* **Splits** them into individual annotated files, preserving the directory structure.

## Installation

To install CodeDump, run:

```bash
pip install codedump
```

Or clone this repository and install locally:

```bash
git clone https://github.com/yourusername/codedump.git
cd codedump
pip install .
```

## Usage

```bash
python codedump.py [directory] [options]
```

* `directory` (optional): Path to process (default: current directory).

### Options

* `-l, --list-only`
  Only list matching file paths without content.

* `-s, --split`
  Instead of one big output, write each file into its own annotated file.

* `--output-dir DIR`
  Root folder in which to place split files (default: `extracted/`).

### Examples

* **Dump all code from the current directory**

  ```bash
  python codedump.py
  ```

* **Dump all code from a specific directory**

  ```bash
  python codedump.py C:\Projects\MyProject
  ```

* **List file paths only**

  ```bash
  python codedump.py --list-only

  python codedump.py C:\Projects\MyProject --list-only
  ```

* **Split into individual annotated files under `extracted/`**

  ```bash
  python codedump.py --split

  python codedump.py C:\Projects\MyProject --split
  ```

* **Split into a custom folder**

  ```bash
  python codedump.py --split --output-dir my_dump

  python codedump.py C:\Projects\MyProject --split --output-dir my_dump
  ```

## What It Does

* **Default mode**

  1. Recursively scans the specified directory.
  2. Finds all code and config files (see “Supported Files” below).
  3. Outputs their contents with headers showing:

     * File path
     * File size in bytes
     * Last modified timestamp
  4. Copies the combined output to your clipboard.

* **Split mode**

  1. Recursively scans the specified directory.
  2. Finds the same set of files.
  3. For each file, writes a separate annotated file under `--output-dir`, preserving its relative path.

## Supported Files & Filters

By default, CodeDump looks for a wide range of source, script, config, and markup extensions (e.g. `.py`, `.js`, `.ts`, `.java`, `.html`, `.md`, `.yaml`, etc.) and also a whitelist of filenames without extensions (e.g. `README`, `Dockerfile`, `package.json`, etc.).

It automatically **skips**:

* Binary files
* Build and distribution directories (`build/`, `dist/`, `target/`, `.next/`, etc.)
* Cache and virtual-env folders (`__pycache__/`, `node_modules/`, `venv/`, etc.)
* Version control metadata (`.git/`, `.svn/`, etc.)
* Log, temp, backup files (`*.log`, `*.tmp`, `*.bak`, swap files, etc.)

Feel free to tweak the whitelists and skip-lists in your copy of `should_skip()`.
