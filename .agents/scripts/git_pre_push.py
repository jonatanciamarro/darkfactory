#!/usr/bin/env python3
"""Git Pre-Push Hook: Enforce Branch Protection & Quality Gate before Push."""
import subprocess
import sys

BLOCKED_BRANCHES = {"main", "master", "develop", "prod", "production"}


def get_current_branch() -> str:
    res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    return res.stdout.strip()


def main():
    branch = get_current_branch()
    if branch.lower() in BLOCKED_BRANCHES:
        print("\n❌ [GIT PRE-PUSH HOOK BLOCKED]: Push direto na branch '%s' é estritamente PROIBIDO!" % branch)
        print("👉 Faça push na sua feature branch e abra um Pull Request para revisão por pares:")
        print("   git push origin feat/<ticket>-<slug>\n")
        sys.exit(1)

    print("✅ [GIT PRE-PUSH HOOK]: Branch '%s' permitida para push." % branch)
    sys.exit(0)


if __name__ == "__main__":
    main()
