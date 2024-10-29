import os
import datetime
import pyperclip
import re
import sys
import argparse  # Add this import

def get_file_info(file_path):
    """Get file information including size and last modified time."""
    stats = os.stat(file_path)
    return {
        'size': stats.st_size,
        'last_modified': datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    }

def should_skip(path):
    """Check if the file or directory should be skipped."""
    name = os.path.basename(path)
    name_lower = name.lower()
    _, extension = os.path.splitext(name)
    
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
        'makefile', 'cmakelist.txt', 'cmakelist.txt',
        # Julia
        'project.toml', 'manifest.toml', 'juliaconfig.toml',
        # JavaScript/TypeScript
        '.npmignore', '.babelrc', '.eslintrc', '.prettierrc', 
        'tslint.json', 'webpack.config.js', 'package-lock.json', 'yarn.lock',
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
    
    if os.path.isdir(path):
        return (name in skip_directories or
                any(re.search(pattern, name) for pattern in skip_directory_patterns))
    
    # Check if the file matches any skip patterns
    if any(re.search(pattern, name_lower) for pattern in skip_patterns):
        return True
    
    return (
        (name.startswith('.') and name_lower not in allowed_filenames) or
        (extension.lower() not in allowed_extensions and name_lower not in allowed_filenames)
    )

def concatenate_files(directory='.', list_only=False):
    """Recursively concatenate all files in the directory and subdirectories with annotations and return as a string."""
    output = []
    for root, dirs, files in os.walk(directory):
        # Remove directories that should be skipped
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]

        for file in files:
            if should_skip(file):
                continue
            
            file_path = os.path.join(root, file)
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
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        output.append(content)
                except Exception as e:
                    output.append(f"Error reading file: {str(e)}")
    
    return '\n'.join(output)

def main():
    parser = argparse.ArgumentParser(description='Concatenate files in a directory.')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to process (default: current directory)')
    parser.add_argument('-l', '--list-only', action='store_true', help='Only list file paths without content')
    
    args = parser.parse_args()
    
    result = concatenate_files(args.directory, args.list_only)
    print(result)
    pyperclip.copy(result)
    print(f"\nOutput for directory '{args.directory}' has been copied to clipboard.")

if __name__ == '__main__':
    main()
