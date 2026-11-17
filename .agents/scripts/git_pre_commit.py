#!/usr/bin/env python3
"""Git Pre-Commit Hook: Enforce Branch Protection & Secret Scanning."""
import os
import re
import subprocess
import sys

BLOCKED_BRANCHES = {"main", "master", "develop", "prod", "production"}

SECRET_PATTERNS = [
    (r'(?i)api[_-]?key\s*[:=]\s*[\'\"][^\'\"]{10,}[\'\"]', 'API Key'),
    (r'(?i)secret\s*[:=]\s*[\'\"][^\'\"]{10,}[\'\"]', 'Secret Key'),
    (r'-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP)? PRIVATE KEY-----', 'Private Key'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub Token'),
    (r'AIza[0-9A-Za-z-_]{35}', 'Google API Key'),
    (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key'),
]


def get_current_branch() -> str:
    res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    return res.stdout.strip()


def check_branch_protection(branch: str) -> bool:
    if branch.lower() in BLOCKED_BRANCHES:
        print("\n❌ [GIT PRE-COMMIT HOOK ERROR]: Commits diretos na branch '%s' são estritamente PROIBIDOS!" % branch)
        print("👉 Em conformidade com a governança corporativa, crie uma feature branch:")
        print("   git checkout -b feat/<ticket>-<slug>\n")
        return False
    return True


def check_staged_secrets() -> bool:
    res = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    staged_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]

    found_violations = []
    for file_path in staged_files:
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for pattern, label in SECRET_PATTERNS:
                if re.search(pattern, content):
                    found_violations.append((file_path, label))
        except Exception:
            pass

    if found_violations:
        print("\n❌ [GIT PRE-COMMIT HOOK ERROR]: Possível vazamento de segredos detectado:")
        for path, label in found_violations:
            print("   - %s: %s" % (path, label))
        print("👉 Remova credenciais e tokens antes de commitar!\n")
        return False

    return True


def main():
    branch = get_current_branch()
    if not check_branch_protection(branch):
        sys.exit(1)

    if not check_staged_secrets():
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
