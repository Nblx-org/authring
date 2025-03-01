import subprocess
import os
import json
import mimetypes
from collections import defaultdict
from radon.complexity import cc_visit
from tree_sitter import Language, Parser
from cassandra.cluster import Cluster
import argparse
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

cloud_config = {'secure_connect_bundle': 'path/to/secure-connect-database_name.zip'}
cluster = Cluster(cloud=cloud_config)
session = cluster.connect()

session.set_keyspace("your_keyspace")
def run_command(command, directory="."):
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=directory)
    return result.stdout.strip() if result.returncode == 0 else ""

def get_earliest_latest_commits(directory, depth):
    depth_arg = f"--max-count={depth}" if depth else ""
    earliest_commit = run_command(f"git rev-list --max-parents=0 HEAD {depth_arg} | tail -1 | xargs git log -n 1 --format='%ad' --date=short", directory)
    latest_commit = run_command(f"git rev-list --all --since=1970-01-01 {depth_arg} | head -1 | xargs git log -n 1 --format='%ad' --date=short", directory)
    return earliest_commit, latest_commit

def get_authors_info(directory, depth):
    authors = {}
    depth_arg = f"--max-count={depth}" if depth else ""
    author_commits = run_command(f"git log --all --format='%an|%ae|%ad' --date=short {depth_arg}", directory)
    for line in author_commits.splitlines():
        name, email, date = line.split('|')
        normalized_name = name.strip().lower()
        if normalized_name not in authors:
            authors[normalized_name] = {"name": name, "email": email, "first_commit": date, "last_commit": date, "commit_count": 0}
        authors[normalized_name]["last_commit"] = date
        authors[normalized_name]["commit_count"] += 1
    return authors

def analyze_python_code(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    complexity_scores = cc_visit(code)
    avg_complexity = sum(c.complexity for c in complexity_scores) / len(complexity_scores) if complexity_scores else 0
    
    parser = Parser()
    parser.set_language(Language("build/tree-sitter-python.so", "python"))
    tree = parser.parse(bytes(code, "utf8"))
    function_calls = len(tree.root_node.children)
    
    return avg_complexity, function_calls

def get_code_metrics(directory):
    metrics = {}
    all_files = run_command("git ls-files", directory).splitlines()
    for file_path in all_files:
        if file_path.endswith(".py"):
            avg_complexity, function_calls = analyze_python_code(file_path)
            metrics[file_path] = {"complexity": avg_complexity, "function_calls": function_calls}
    return metrics

def store_in_astra(data):
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect("git_analysis")
    query = """
    INSERT INTO code_metrics (author, email, file, complexity, function_calls, commit_count)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    for author in data["authors"]:
        for file, metrics in data["metrics"].items():
            session.execute(query, (author["name"], author["email"], file, metrics["complexity"], metrics["function_calls"], author["commit_count"]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Git repository statistics and code complexity.")
    parser.add_argument("--directory", default=".", help="Path to the Git repository (defaults to current directory)")
    parser.add_argument("--depth", type=int, default=None, help="Maximum number of commits to analyze (defaults to all)")
    args = parser.parse_args()
    
    earliest, latest = get_earliest_latest_commits(args.directory, args.depth)
    authors_info = get_authors_info(args.directory, args.depth)
    metrics = get_code_metrics(args.directory)
    
    output = {
        "earliest_commit": earliest,
        "latest_commit": latest,
        "authors": list(authors_info.values()),
        "metrics": metrics
    }
    
    print(json.dumps(output, indent=4))
    store_in_astra(output)
