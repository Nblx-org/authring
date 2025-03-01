#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import subprocess
import argparse
import json
#from cassandra.cluster import Cluster
#from cassandra.auth import PlainTextAuthProvider
import tree_sitter
from tree_sitter import Language, Parser
import tempfile
import shutil

from astrapy import DataAPIClient
import uuid
import os

import requests
import json


def run_command(command):
    """Executes a shell command and returns the output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.stdout

def clone_repository(repo_url):
    """Clones the remote Git repository into a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    print(f"Cloning repository into {temp_dir}...")
    command = f"git clone {repo_url} {temp_dir}"
    run_command(command)
    return temp_dir

def analyze_repository(repo_url, depth=None):
    """Analyzes a remote Git repository by cloning it and running 'git log'."""
    
    # Clone the repository into a temporary directory
    temp_dir = clone_repository(repo_url)

    try:
        # Ensure the directory is a valid Git repository
        if not os.path.exists(os.path.join(temp_dir, ".git")):
            print(f"Error: The cloned directory '{temp_dir}' is not a Git repository.")
            return None

        depth_arg = f"--max-count={depth}" if depth else ""
        log_output = run_command(f"git -C {temp_dir} log {depth_arg} --pretty=format:'%H %an %ae' --name-only")

        if not log_output:
            print("Error: Unable to retrieve Git logs.")
            return None

        authors_info = {}
        file_complexity = {}
        commit_count = {}

        lines = log_output.split('\n')
        current_commit = None
        for line in lines:
            if line.strip():
                parts = line.split()
                #print(parts)
                if len(parts) != 1:  # Commit hash, author name, email
                    commit_hash=parts[0]
                    email=parts[len(parts)-1]
                    author=" ".join(parts[1:len(parts)-1])
                    current_commit = commit_hash
                    if email not in authors_info:
                        authors_info[email] = {"author": author, "email": email, "commit_count": 0}
                    authors_info[email]["commit_count"] += 1
                else:  # File name
                    file = line.strip()
                    if file not in file_complexity:
                        file_complexity[file] = 0
                        commit_count[file] = 0
                    file_complexity[file] = 1
                    commit_count[file] += 1

        # Cleanup: Remove the temporary directory
        shutil.rmtree(temp_dir)
        return {
            "authors": list(authors_info.values()),
            "files": [
                {"file": f, "complexity": file_complexity[f], "commit_count": commit_count[f]} for f in file_complexity
            ],
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

def count_function_calls(file_path):
    LANGUAGE_PATH = 'tree-sitter-python.so'
    if not os.path.exists(LANGUAGE_PATH):
        print("Error: Missing Tree-sitter language file.")
        return 0
    
    Language.build_library(
        LANGUAGE_PATH,
        ["tree-sitter-python"]
    )
    PY_LANGUAGE = Language(LANGUAGE_PATH, "python")
    parser = Parser()
    parser.set_language(PY_LANGUAGE)
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return 0
    
    tree = parser.parse(bytes(code, "utf8"))
    query = PY_LANGUAGE.query("(call function: (identifier) @function_call)")
    captures = query.captures(tree.root_node)
    
    return len(captures)

def store_in_astra(data):
    load_dotenv()
    url = os.getenv("URL")
    key =os.getenv("KEY")
    headers = {
    "X-Cassandra-Token": key,
    "Content-Type": "application/json"
    }

# Data to be inserted
    data = {
    "author": "Mookie",
    "email": "mookie.betts@gmail.com",
    "file": "Mookie",
    "complexity": 1,
    "function_calls": 1,
    "commit_count": 1
    }

# Send the POST request to insert the data
    response = requests.post(url, headers=headers, data=json.dumps(data))

# Handle the response
    if response.status_code == 201:
        print("Data successfully posted!")
    else:
        print(f"Failed to post data. Status code: {response.status_code}, Error: {response.text}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, help="Path to the Git repository")
    parser.add_argument("--depth", type=int, help="Maximum number of commits to analyze")
    args = parser.parse_args()
    
    analysis_data = analyze_repository(args.directory, args.depth)
    if analysis_data:
        store_in_astra(analysis_data)
        print(json.dumps(analysis_data, indent=2))
    else:
        print("No valid data to store.")

if __name__ == "__main__":
    main()
