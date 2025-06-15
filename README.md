# CodeDump

CodeDump is a simple Python tool that concatenates and dumps code from a directory, including file information such as size and last modified time.

## Installation

To install CodeDump, run:

    pip install codedump

Or clone this repository and run:

    pip install .

## Usage

CodeDump can be used from the command line:

# Dump all code files from current directory

    codedump

# Dump all code files from a specific directory

    codedump /path/to/directory

# Example command:

    python codedump.py C:\Projects\ProjectName

# Only list file paths without content

    python codedump.py -l
    python codedump.py --list-only

The tool will:
1. Recursively scan the specified directory
2. Find all code and configuration files
3. Output their contents with file information
4. Automatically copy the output to your clipboard

CodeDump automatically filters out:
- Binary files
- Build directories
- Cache directories
- Version control directories
- Log files
- Temporary files
