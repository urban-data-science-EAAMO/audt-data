"""
[augmented urban data triangulation (audt)]
[audt-data]
[Check Headers]
[Script for check headers]
[Matt Franchi]
"""

#!/usr/bin/env python3
"""
Script to automatically check for and add headers to code files.
"""
import os
import re
import sys
import datetime
import git
import argparse
from pathlib import Path

# Define the expected header format based on README guidelines
HEADER_TEMPLATES = {
    '.py': '''"""
[augmented urban data triangulation (audt)]
[{repo_name}]
[{short_title}]
[{description}]
[{authors}]
"""

''',
    '.sh': '''#!/bin/bash
# [augmented urban data triangulation (audt)]
# [{repo_name}]
# [{short_title}]
# [{description}]
# [{authors}]

''',
    '.js': '''/**
 * [augmented urban data triangulation (audt)]
 * [{repo_name}]
 * [{short_title}]
 * [{description}]
 * [{authors}]
 */

''',
    '.ts': '''/**
 * [augmented urban data triangulation (audt)]
 * [{repo_name}]
 * [{short_title}]
 * [{description}]
 * [{authors}]
 */

''',
    '.R': '''#
# [augmented urban data triangulation (audt)]
# [{repo_name}]
# [{short_title}]
# [{description}]
# [{authors}]
#

'''
}

# Default header for other file types
DEFAULT_HEADER = '''# [augmented urban data triangulation (audt)]
# [{repo_name}]
# [{short_title}]
# [{description}]
# [{authors}]

'''

# Function to check if a file has a header based on its extension
def has_header(content, file_ext):
    if file_ext == '.py':
        pattern = r'^""".*?"""'
        return bool(re.match(pattern, content, re.DOTALL))
    elif file_ext == '.sh':
        pattern = r'^#!/bin/bash\s*\n# \[augmented urban data triangulation'
        return bool(re.search(pattern, content))
    elif file_ext in ['.js', '.ts']:
        pattern = r'^/\*\*.*?\*/\s*'
        return bool(re.match(pattern, content, re.DOTALL))
    elif file_ext == '.R':
        pattern = r'^#\s*\n# \[augmented urban data triangulation'
        return bool(re.search(pattern, content))
    else:
        # Generic pattern for comment-based headers
        pattern = r'^# \[augmented urban data triangulation'
        return bool(re.search(pattern, content))

# Function to generate a description based on the file content
def generate_description(content, filename, file_ext):
    # Look for main functions or classes to guess the purpose based on file type
    if file_ext == '.py':
        main_funcs = re.findall(r'def\s+(\w+)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        
        if "main" in main_funcs:
            return f"Script for {' '.join(filename.stem.split('_'))}"
        elif classes:
            return f"Module containing {', '.join(classes)} classes for {' '.join(filename.stem.split('_'))}"
        elif main_funcs:
            return f"Module with functions for {' '.join(filename.stem.split('_'))}"
    elif file_ext == '.sh':
        return f"Shell script for {' '.join(filename.stem.split('_'))}"
    elif file_ext in ['.js', '.ts']:
        classes = re.findall(r'class\s+(\w+)', content)
        functions = re.findall(r'function\s+(\w+)', content)
        
        if classes:
            return f"JavaScript/TypeScript module with {', '.join(classes)} classes"
        elif functions:
            return f"JavaScript/TypeScript module with utility functions"
    elif file_ext == '.R':
        return f"R script for {' '.join(filename.stem.split('_'))}"
    
    # Default description
    return f"Code related to {' '.join(filename.stem.split('_'))}"

# Function to generate a short title from the filename
def generate_short_title(filename):
    return ' '.join(word.capitalize() for word in filename.stem.split('_'))

# Function to find the nearest Git repository by traversing up the directory tree
def find_git_repo(path):
    current_path = Path(path).absolute()
    
    while current_path != current_path.parent:  # Stop at the root directory
        try:
            return git.Repo(current_path)
        except git.exc.InvalidGitRepositoryError:
            current_path = current_path.parent
    
    # If we reach here, no Git repository was found
    return None

# Function to get repository name
def get_repo_name(repo):
    if repo is None:
        # Use current directory name as a fallback
        return os.path.basename(os.getcwd())
        
    try:
        # Extract repo name from remote URL
        remote_url = repo.remotes.origin.url
        repo_name = os.path.basename(remote_url)
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        return repo_name
    except:
        # If we can't get the repo name, use the parent directory name
        return os.path.basename(os.path.dirname(repo.working_dir if repo else os.getcwd()))

# Function to get author information with GitHub username if available
def get_author(repo, file_path):
    if repo is None:
        return "Test User (@testuser)"  # Provide a default for testing
    
    try:
        # Try to get the author of the first commit for this file
        author_name = None
        author_email = None
        
        for commit in repo.iter_commits(paths=file_path, max_count=1, reverse=True):
            author_name = commit.author.name
            author_email = commit.author.email
            break
        
        if not author_name:
            return "Unknown"
        
        # Try to extract GitHub username from email or config
        github_username = None
        if author_email and "@github" in author_email:
            github_username = author_email.split('@')[0]
        
        if github_username:
            return f"{author_name} (@{github_username})"
        else:
            return author_name
    except:
        # Default if git info not available
        return "Unknown"

# Function to add header to a file
def add_header(file_path, repo):
    with open(file_path, 'r') as f:
        content = f.read()
    
    file_ext = Path(file_path).suffix.lower()
    
    if has_header(content, file_ext):
        return False  # Header already exists
    
    # Generate header info
    filename = Path(file_path)
    description = generate_description(content, filename, file_ext)
    authors = get_author(repo, file_path)
    repo_name = get_repo_name(repo)
    short_title = generate_short_title(filename)
    
    # Select the appropriate header template
    header_template = HEADER_TEMPLATES.get(file_ext, DEFAULT_HEADER)
    
    # Format the header
    header = header_template.format(
        repo_name=repo_name,
        short_title=short_title,
        description=description,
        authors=authors
    )
    
    # For shell scripts, make sure shebang is preserved if it exists
    if file_ext == '.sh' and content.startswith('#!/'):
        shebang_line = content.split('\n', 1)[0] + '\n'
        content = content.split('\n', 1)[1] if '\n' in content else ''
        header = shebang_line + header.replace('#!/bin/bash\n', '')
    
    # Add the header to the file
    with open(file_path, 'w') as f:
        f.write(header + content)
    
    return True  # Header was added

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Check and add headers to code files')
    parser.add_argument('--exclude', nargs='+', help='Files to exclude from processing')
    args, unknown_args = parser.parse_known_args()
    
    excluded_files = set(args.exclude if args.exclude else [])
    # Always exclude README.md
    excluded_files.add('README.md')
    
    # If additional arguments are provided, use them as file paths to check
    if unknown_args:
        file_paths = unknown_args
    else:
        # Find all supported code files in the repository
        file_paths = []
        supported_extensions = tuple(HEADER_TEMPLATES.keys()) + ('.md',)  # Add any other extensions
        for root, _, files in os.walk('.'):
            if '.git' in root or '.github' in root:
                continue
            for file in files:
                if file.endswith(supported_extensions) and file not in excluded_files:
                    file_paths.append(os.path.join(root, file))
    
    # Try to initialize git repo from current directory or by searching upwards
    try:
        repo = git.Repo('.')
    except git.exc.InvalidGitRepositoryError:
        print("Warning: Not in a Git repository. Searching for nearest Git repository...")
        repo = find_git_repo(os.getcwd())
        if repo:
            print(f"Found Git repository at: {repo.working_dir}")
        else:
            print("No Git repository found. Using default values for headers.")
    
    # Process each file
    headers_added = 0
    for file_path in file_paths:
        # Skip excluded files
        if os.path.basename(file_path) in excluded_files:
            continue
            
        if add_header(file_path, repo):
            print(f"Added header to {file_path}")
            headers_added += 1
    
    print(f"Processed {len(file_paths)} files, added {headers_added} headers")

if __name__ == "__main__":
    main()