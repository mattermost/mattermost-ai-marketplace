#!/usr/bin/env python3
"""Save the reviewer definitions of a security review to disk, exactly as the pipeline assembled them.

Usage: materialize_definitions.py <commit> <output dir> <path>=<sha256> [<path>=<sha256> ...]

Each <path> is relative to plugins/security-pr-review/ (for example agents/pr-paranoid-reviewer.md).
The file is fetched at <commit>, and every line that is only @<relative path> is replaced by the content of
that file (relative to the file that contains it, front matter removed, recursively), the same way the
pipeline builds the prompt. The result is written to <output dir>/<path> and its SHA-256 must equal the
expected one. Nothing is rewritten or summarized, and the exit code is not 0 if any file differs.
"""
import hashlib
import os
import re
import sys
import urllib.request

REPO = "mattermost/mattermost-ai-marketplace"
ROOT = "plugins/security-pr-review/"
MAX_DEPTH = 8


def load(commit, path):
    url = "https://raw.githubusercontent.com/%s/%s/%s" % (REPO, commit, path)
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read().decode("utf-8")


def norm(path):
    out = []
    for segment in path.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if not out:
                raise SystemExit("an import escapes the repository: " + path)
            out.pop()
        else:
            out.append(segment)
    return "/".join(out)


def strip_front_matter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            return text[end + 5:]
    return text


def resolve(commit, path, depth=0, stack=()):
    if depth > MAX_DEPTH:
        raise SystemExit("imports are nested too deep at " + path)
    if path in stack:
        raise SystemExit("circular import at " + path)
    out = []
    for raw in strip_front_matter(load(commit, path)).split("\n"):
        line = raw[:-1] if raw.endswith("\r") else raw
        match = re.match(r"^@(\S+)$", line)
        if match:
            target = norm(path[: path.rfind("/") + 1] + match.group(1))
            if not target.startswith(ROOT):
                raise SystemExit("an import points outside the plugin: " + target)
            out.append(resolve(commit, target, depth + 1, stack + (path,)))
        else:
            out.append(line)
    return "\n".join(out)


def main(argv):
    if len(argv) < 4:
        raise SystemExit(__doc__)
    commit, out_dir = argv[1], argv[2]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SystemExit("the commit must be a full SHA")
    failed = False
    for entry in argv[3:]:
        path, _, expected = entry.partition("=")
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", path) or ".." in path or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise SystemExit("invalid entry: " + entry)
        data = resolve(commit, ROOT + path).encode("utf-8")
        actual = hashlib.sha256(data).hexdigest()
        target = os.path.join(out_dir, path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.exists(target):
            os.remove(target)
        with open(target, "wb") as handle:
            handle.write(data)
        os.chmod(target, 0o444)
        ok = actual == expected
        failed = failed or not ok
        print("%s %s sha256=%s bytes=%d" % ("OK      " if ok else "MISMATCH", target, actual, len(data)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv)
