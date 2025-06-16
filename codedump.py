import os
import datetime
import pyperclip
import re
import sys
import argparse

def get_file_info(file_path):
    """Get file information including size and last modified time."""
    try:
        stats = os.stat(file_path)
        return {
            'size': stats.st_size,
            'last_modified': datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    except FileNotFoundError:
        return {
            'size': 'N/A',
            'last_modified': 'N/A'
        }

def should_skip(path):
    """Check if the file or directory should be skipped."""
    # List of allowed extensions
    allowed_extensions = {
        # General
        '.txt', '.md', '.markdown', '.json', '.xml', '.yaml', '.yml', '.toml',
        '.ini', '.cfg', '.conf', '.sql', '.graphql', '.proto',
        # Python
        '.py', '.pyx', '.pyd', '.pyo', '.pyc', '.pyw', '.pyi',
        # C and C++
        '.c', '.h', '.i', '.cpp', '.hpp', '.cc', '.hh', '.cxx', '.hxx',
        # Julia
        '.jl',
        # JavaScript and TypeScript
        '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
        # Web
        '.html', '.htm', '.css', '.scss', '.sass', '.less',
        # Java and JVM languages
        '.java', '.kt', '.kts', '.groovy', '.scala', '.clj', '.cljs',
        # .NET languages
        '.cs', '.fs', '.vb',
        # Ruby
        '.rb', '.rake', '.gemspec',
        # PHP
        '.php', '.phtml', '.php3', '.php4', '.php5', '.phps',
        # Go
        '.go',
        # Rust
        '.rs',
        # Swift
        '.swift',
        # Shell scripting
        '.sh', '.bash', '.zsh', '.fish',
        # PowerShell
        '.ps1', '.psm1', '.psd1',
        # Perl
        '.pl', '.pm',
        # Lua
        '.lua',
        # Haskell
        '.hs', '.lhs',
        # R
        '.r', '.R', '.Rmd',
        # Dart
        '.dart',
        # Kotlin
        '.kt', '.kts',
        # Objective-C
        '.m', '.mm',
        # Elm
        '.elm',
        # F#
        '.fs', '.fsi', '.fsx',
        # Elixir
        '.ex', '.exs',
        # Erlang
        '.erl', '.hrl',
        # Lisp dialects
        '.lisp', '.cl', '.el',
        # Fortran
        '.f', '.for', '.f90', '.f95', '.f03', '.f08',
        # MATLAB/Octave
        '.m', '.mat',
        # Scala
        '.scala', '.sc',
        # Terraform
        '.tf', '.tfvars',
        # Ansible
        '.yml', '.yaml',
        # LaTeX
        '.tex', '.sty', '.cls',
    }

    # List of allowed filenames without extensions
    allowed_filenames = {
        # General
        'readme', 'license', 'dockerfile', 'makefile', '.gitignore', '.dockerignore',
        '.editorconfig', '.env', 'requirements.txt', 'package.json', 'tsconfig.json',
        # Python
        'setup.py', 'setup.cfg', 'pyproject.toml', 'pipfile', 'manifest.in',
        '.pylintrc', '.flake8', 'pytest.ini', 'tox.ini',
        # C/C++
        'makefile', 'cmakelist.txt', 'cmakelists.txt',
        # Julia
        'project.toml', 'manifest.toml', 'juliaconfig.toml',
        # JavaScript/TypeScript
        '.npmignore', '.babelrc', '.eslintrc', '.prettierrc',
        'tslint.json', 'webpack.config.js', 'yarn.lock',
        # Ruby
        'gemfile', 'rakefile',
        # PHP
        'composer.json', 'composer.lock',
        # Go
        'go.mod', 'go.sum',
        # Rust
        'cargo.toml', 'cargo.lock',
        # .NET
        'packages.config', 'nuget.config',
        # Java
        'pom.xml', 'build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts',
        # Docker
        'docker-compose.yml', 'docker-compose.yaml',
        # Git
        '.gitattributes',
        # CI/CD
        '.travis.yml', '.gitlab-ci.yml', 'jenkins.file', 'azure-pipelines.yml',
        # Editor/IDE
        '.vscode', '.idea',
        # Elm
        'elm.json',
        # F#
        'paket.dependencies', 'paket.lock',
        # Elixir
        'mix.exs', 'mix.lock',
        # Erlang
        'rebar.config',
        # MATLAB/Octave
        '.octaverc',
        # Scala
        'build.sbt',
        # Terraform
        '.terraform.lock.hcl',
        # Ansible
        'ansible.cfg', 'hosts',
        # LaTeX
        'latexmkrc',
    }

    # Directories to skip
    skip_directories = {
        '__pycache__', 'node_modules', 'venv', 'env', '.venv', '.env',
        'build', 'dist', 'target', 'out', 'bin', 'obj',
        '.git', '.svn', '.hg',  # Version control directories
        '.idea', '.vscode',  # IDE directories
        'logs',  # Log directories
        'output',  # Output directories
        '.next', # ADDED: Directory for Next.js builds
    }

    # A new set for specific filenames to skip
    skip_filenames = {
        'package-lock.json',
    }

    # Regex patterns for directories to skip
    skip_directory_patterns = [
        r'\.egg-info$',  # Matches directories ending with .egg-info
    ]

    # Regex patterns for files to skip
    skip_patterns = [
        r'\.log(\.[0-9]+)?$',  # Matches .log, .log.1, .log.2, etc.
        r'^log\.',  # Matches log.txt, log.old, etc.
        r'\.bak$',
        r'\.tmp$',
        r'\.temp$',
        r'\.swp$',
        r'~$',
    ]

    # First, check if any part of the path is a directory that should be skipped.
    try:
        path_parts = set(os.path.normpath(path).split(os.sep))
        if not path_parts.isdisjoint(skip_directories):
            return True
    except Exception:
        pass

    name = os.path.basename(path)
    name_lower = name.lower()
    _, extension = os.path.splitext(name)

    # Check directories against regex patterns
    if os.path.isdir(path):
        return any(re.search(pattern, name) for pattern in skip_directory_patterns)

    # Check if the filename is in the explicit skip list
    if name_lower in skip_filenames:
        return True

    # Check if the file matches any general skip patterns
    if any(re.search(pattern, name_lower) for pattern in skip_patterns):
        return True

    # Final check based on allowed extensions and filenames
    return (
        (name.startswith('.') and name_lower not in allowed_filenames) or
        (extension.lower() not in allowed_extensions and name_lower not in allowed_filenames)
    )

def concatenate_files(directory='.', list_only=False):
    """Recursively concatenate all files in the directory and subdirectories with annotations and return as a string."""
    output = []
    for root, dirs, files in os.walk(directory, topdown=True):
        # Prune the directories to search. This is the most efficient way.
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]

        for file in files:
            file_path = os.path.join(root, file)
            # This check is now redundant if directory pruning is perfect, but acts as a good failsafe.
            if should_skip(file_path):
                continue

            file_info = get_file_info(file_path)

            if list_only:
                output.append(f"{file_path}")
            else:
                output.append(f"\n\n{'=' * 80}")
                output.append(f"File: {file_path}")
                output.append(f"Size: {file_info['size']} bytes")
                output.append(f"Last Modified: {file_info['last_modified']}")
                output.append('=' * 80 + '\n')

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        output.append(content)
                except Exception as e:
                    output.append(f"Error reading file: {str(e)}")

    return '\n'.join(output)

def split_files(directory='.', output_dir='extracted'):
    """Recursively write each relevant file into its own annotated file."""
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]

        for file in files:
            src_path = os.path.join(root, file)
            if should_skip(src_path):
                continue

            # Build annotated header + content
            info = get_file_info(src_path)
            header = (
                f"{'=' * 80}\n"
                f"File: {src_path}\n"
                f"Size: {info['size']} bytes\n"
                f"Last Modified: {info['last_modified']}\n"
                f"{'=' * 80}\n\n"
            )
            try:
                with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
                    body = f.read()
            except Exception as e:
                body = f"Error reading file: {e}"

            annotated = header + body

            # Determine destination path
            rel = os.path.relpath(src_path, directory)
            dest_path = os.path.join(output_dir, rel)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Write file
            with open(dest_path, 'w', encoding='utf-8') as out_f:
                out_f.write(annotated)

    print(f"\nAll files have been split into '{output_dir}/'.")

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description='Concatenate or split files in a directory.')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to process (default: current directory)')
    parser.add_argument('-l', '--list-only', action='store_true', help='Only list file paths without content')
    parser.add_argument('-s', '--split', action='store_true', help='Split each file into its own annotated file')
    parser.add_argument('--output-dir', default='extracted', help='Folder in which to place split files (default: extracted/)')

    args = parser.parse_args()

    if args.split:
        split_files(args.directory, args.output_dir)
    else:
        result = concatenate_files(args.directory, args.list_only)
        print(result)
        try:
            pyperclip.copy(result)
            print(f"\nOutput for directory '{args.directory}' has been copied to clipboard.")
        except pyperclip.PyperclipException:
            pass

if __name__ == '__main__':
    main()
