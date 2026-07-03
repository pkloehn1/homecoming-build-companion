#!/usr/bin/env python3
"""Report a required status context using the GitHub CLI.

Used by the report-status-context composite action on Windows runners
(via ``python -m scripts.ci.report_status_context``). On Linux runners,
the bash script ``scripts/ci/report_status_context.sh`` is used instead.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report a required status context to merge_commit_sha")
    parser.add_argument("--github-token", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--job-status", required=True)
    parser.add_argument("--status-context", required=True)
    parser.add_argument("--target-url", required=True)
    return parser.parse_args(argv)


def _job_status_to_state(job_status: str) -> str:
    normalized = (job_status or "").strip().lower()
    if normalized == "success":
        return "success"
    if normalized == "failure":
        return "failure"
    return "error"


def _run_gh(args: list[str], env: dict[str, str]) -> str:
    result = subprocess.run(
        args,
        check=False,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr_text = result.stderr or ""
        message = f"gh command failed with exit code {result.returncode}. stderr:\n{stderr_text.rstrip()}"
        raise RuntimeError(message)
    return result.stdout.strip()


def main(argv: list[str]) -> int:
    """Main."""
    args = _parse_args(argv)

    repo = (os.environ.get("GITHUB_REPOSITORY") or "").strip()
    if not repo:
        print("Error: GITHUB_REPOSITORY is required (owner/repo)", file=sys.stderr)
        return 2

    env = dict(os.environ)
    env["GH_TOKEN"] = args.github_token

    try:
        sha = _run_gh(
            [
                "gh",
                "api",
                f"repos/{repo}/pulls/{args.pr_number}",
                "--jq",
                ".head.sha",
            ],
            env=env,
        )
    except RuntimeError as exc:
        print(f"Error resolving head SHA for PR #{args.pr_number}: {exc}", file=sys.stderr)
        return 2

    if not sha or sha == "null":
        print(
            f"Error: No head SHA available for PR #{args.pr_number} in {repo}. "
            "The PR may not exist or the API response is missing .head.sha.",
            file=sys.stderr,
        )
        return 2

    state = _job_status_to_state(args.job_status)
    description = f"Reported by GitHub Actions ({args.job_status})"

    print(
        f"Posting status context '{args.status_context}' (state={state}) to {repo}@{sha[:12]}",
        file=sys.stderr,
    )

    try:
        _run_gh(
            [
                "gh",
                "api",
                "-X",
                "POST",
                f"repos/{repo}/statuses/{sha}",
                "-f",
                f"state={state}",
                "-f",
                f"context={args.status_context}",
                "-f",
                f"description={description}",
                "-f",
                f"target_url={args.target_url}",
            ],
            env=env,
        )
    except RuntimeError as exc:
        print(
            f"Error posting status context '{args.status_context}' to {repo}@{sha[:12]}: {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
