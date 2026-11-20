#!/usr/bin/env python3
"""
pr_automator.py - Automated Corporate Branch & Pull Request Generator for corp-pipeline Phase 5.
Creates feature branch, commits changes, pushes to remote (if configured),
and automatically creates Pull Request using GitHub CLI (gh) with delivery markdown body.
"""

import argparse
import subprocess
import sys
from pathlib import Path


import os


def run_cmd(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    git_dir = r"C:\Program Files\Git\cmd"
    gh_dir = r"C:\Program Files\GitHub CLI"
    curr_path = env.get("PATH", "")
    if git_dir not in curr_path:
        curr_path = f"{git_dir};{curr_path}"
    if gh_dir not in curr_path:
        curr_path = f"{gh_dir};{curr_path}"
    env["PATH"] = curr_path

    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=check,
        env=env,
    )


def find_git_exe() -> str:
    # Try finding git in known paths or system PATH
    common_paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
    ]
    for p in common_paths:
        if Path(p).exists():
            return p
    return "git"


def find_gh_exe() -> str:
    common_paths = [
        r"C:\Program Files\GitHub CLI\gh.exe",
    ]
    for p in common_paths:
        if Path(p).exists():
            return p
    return "gh"


def automate_pr(
    workspace_root: Path,
    ticket_id: str,
    slug: str,
    title: str,
    body_file: Path,
    base_branch: str = "main",
) -> None:
    git_bin = find_git_exe()
    gh_bin = find_gh_exe()

    branch_name = f"feat/{ticket_id}-{slug}"
    print(f"🌿 1. Preparando branch corporativa: {branch_name} ...")

    # Check current branch
    res_branch = run_cmd([git_bin, "branch", "--show-current"], cwd=workspace_root)
    current_branch = res_branch.stdout.strip()

    if current_branch != branch_name:
        # Check if branch exists
        res_check = run_cmd([git_bin, "branch", "--list", branch_name], cwd=workspace_root)
        if branch_name in res_check.stdout:
            run_cmd([git_bin, "checkout", branch_name], cwd=workspace_root)
        else:
            run_cmd([git_bin, "checkout", "-b", branch_name], cwd=workspace_root)
        print(f"   ✓ Alternado para a branch: {branch_name}")
    else:
        print(f"   ✓ Já posicionado na branch: {branch_name}")

    # Check for changes to commit
    res_status = run_cmd([git_bin, "status", "--porcelain"], cwd=workspace_root)
    if res_status.stdout.strip():
        print("💾 2. Realizando commit semântico corporativo ...")
        run_cmd([git_bin, "add", "."], cwd=workspace_root)
        run_cmd([git_bin, "commit", "-m", title], cwd=workspace_root)
        print("   ✓ Commit atômico registrado.")
    else:
        print("   ✓ Nenhuma alteração pendente de commit.")

    # Check if remote 'origin' exists
    res_remote = run_cmd([git_bin, "remote"], cwd=workspace_root)
    remotes = [r.strip() for r in res_remote.stdout.splitlines() if r.strip()]

    if "origin" not in remotes:
        print("\n⚠️  Remote 'origin' ainda não configurado no repositório local.")
        print(f"   O arquivo de Pull Request está pronto em: {body_file.resolve()}")
        print("   Assim que conectar ao GitHub (`gh repo create`), o PR poderá ser aberto com:")
        print(f'   & "{gh_bin}" pr create --title "{title}" --body-file "{body_file}" --base "{base_branch}" --head "{branch_name}"')
        return

    # Push to origin
    print(f"🚀 3. Realizando push da branch {branch_name} para origin ...")
    res_push = run_cmd([git_bin, "push", "-u", "origin", branch_name], cwd=workspace_root, check=False)
    if res_push.returncode != 0:
        print(f"   ❌ Falha no push: {res_push.stderr.strip()}")
        return
    print("   ✓ Push concluído com sucesso.")

    # Create PR via gh CLI
    print(f"📋 4. Abrindo Pull Request via GitHub CLI ({gh_bin}) ...")
    if not body_file.exists():
        print(f"   ❌ Arquivo de descrição do PR não encontrado: {body_file}")
        return

    cmd_pr = [
        gh_bin, "pr", "create",
        "--title", title,
        "--body-file", str(body_file),
        "--base", base_branch,
        "--head", branch_name,
    ]
    res_pr = run_cmd(cmd_pr, cwd=workspace_root, check=False)
    if res_pr.returncode == 0:
        print("\n🎉 ✅ PULL REQUEST ABERTO COM SUCESSO!")
        print(f"🔗 URL: {res_pr.stdout.strip()}")
    else:
        # Check if PR already exists
        if "already exists" in res_pr.stderr.lower():
            print("\nℹ️  Pull Request já existe para esta branch.")
            run_cmd([gh_bin, "pr", "view", "--web"], cwd=workspace_root, check=False)
        else:
            print(f"\n❌ Erro ao criar PR via gh: {res_pr.stderr.strip()}")


def main():
    parser = argparse.ArgumentParser(description="Automate Branch and PR creation for corp-pipeline Phase 5")
    parser.add_argument("--ticket-id", required=True, help="Ticket ID (e.g. CORP-001)")
    parser.add_argument("--slug", required=True, help="Feature slug (e.g. autonomous-corporate-engineer)")
    parser.add_argument("--title", required=True, help="Semantic PR and commit title")
    parser.add_argument("--body-file", required=True, help="Path to markdown body file")
    parser.add_argument("--base-branch", default="main", help="Target base branch (default: main)")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")

    args = parser.parse_args()

    automate_pr(
        workspace_root=Path(args.workspace).resolve(),
        ticket_id=args.ticket_id,
        slug=args.slug,
        title=args.title,
        body_file=Path(args.body_file).resolve(),
        base_branch=args.base_branch,
    )


if __name__ == "__main__":
    main()
