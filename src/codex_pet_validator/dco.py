from __future__ import annotations

import argparse
import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass

SIGNOFF_PATTERN = re.compile(r"^Signed-off-by:\s+.+\s+<[^<>]+>\s*$", re.MULTILINE)


@dataclass(frozen=True)
class CommitMessage:
    sha: str
    body: str

    @property
    def signed_off(self) -> bool:
        return SIGNOFF_PATTERN.search(self.body) is not None


def parse_git_log(raw: str) -> list[CommitMessage]:
    messages: list[CommitMessage] = []
    for record in raw.split("\x1e"):
        clean = record.strip()
        if not clean:
            continue
        sha, separator, body = clean.partition("\x00")
        if not separator:
            raise ValueError("git log record is missing a NUL separator")
        messages.append(CommitMessage(sha.strip(), body.strip()))
    return messages


def commits_between(base: str, head: str) -> list[CommitMessage]:
    result = subprocess.run(
        ["git", "log", "--format=%H%x00%B%x1e", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return parse_git_log(result.stdout)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Require DCO sign-off on each commit")
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    commits = commits_between(args.base, args.head)
    if not commits:
        print("No commits found in the pull request range.")
        return 1
    unsigned = [commit.sha for commit in commits if not commit.signed_off]
    if unsigned:
        print("DCO sign-off is missing from:")
        for sha in unsigned:
            print(f"- {sha}")
        print("Amend each commit with: git commit --amend -s")
        return 1
    print(f"PASS: {len(commits)} commit(s) include DCO sign-off.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
