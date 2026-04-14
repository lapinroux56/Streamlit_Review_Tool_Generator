import subprocess


def run_git_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def get_current_branch():
    return run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])


def get_merge_base(branch):
    return run_git_command(["git", "merge-base", "main", branch])


def get_branch_url(base_url, branch, provider):
    if provider == "github":
        return f"{base_url}/tree/{branch}"
    elif provider == "gitlab":
        return f"{base_url}/-/tree/{branch}"
    return base_url


def get_commits(branch):
    merge_base = get_merge_base(branch)

    log_format = "%H|%s|%ci"

    raw = run_git_command([
        "git",
        "log",
        f"{merge_base}..{branch}",
        "--pretty=format:" + log_format
    ])

    commits = []

    for line in raw.split("\n"):
        if not line:
            continue

        commit_hash, message, date = line.split("|", 2)

        files = run_git_command([
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit_hash
        ]).split("\n")

        files = [f.strip() for f in files if f.strip()]

        commits.append({
            "hash": commit_hash,
            "message": message,
            "date": date,
            "files": files
        })

    return commits