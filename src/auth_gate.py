#!/usr/bin/env python3
"""DarkFactory Pre-Flight Authentication & Session Gate.

Enforces persistent authenticated sessions for:
1. Google Flow (flow.google.com) — Gemini Omni Flash 1.2 & DeepMind Veo 3.1
2. RunningHub (runninghub.ai) — Accounts 4 (CosyVoice), 5 (MiniMax Music), 7 (MiniMax H3)

Operational Rules:
- Before any asset (video, audio, foley, motion) is generated in the pipeline,
  the orchestrator verifies that persistent sessions are authenticated.
- If a session is missing or expired, the gate automatically launches a headful
  Chromium browser window for 1-time manual login by the operator, polls for success,
  and saves storage_state.json and browser profiles.
- Subsequent pipeline runs operate completely headless with persistent cookies.
"""
import argparse
import json
import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# ADR-01: Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("DarkFactory Pre-Flight Auth Gate")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AuthGate")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROME_SESSIONS_DIR = PROJECT_ROOT / "chrome_session"
GOOGLE_FLOW_SESSION_DIR = CHROME_SESSIONS_DIR / "google_flow"
RUNNINGHUB_SESSION_DIR = CHROME_SESSIONS_DIR / "runninghub"
FLOWMUSIC_SESSION_DIR = CHROME_SESSIONS_DIR / "flowmusic"

GOOGLE_FLOW_URL = os.getenv("GOOGLE_FLOW_URL", "https://flow.google.com")
RUNNINGHUB_URL = os.getenv("RUNNINGHUB_URL", "https://www.runninghub.ai")
FLOWMUSIC_URL = os.getenv("FLOWMUSIC_URL", "https://www.flowmusic.app/")


def ensure_session_dirs() -> None:
    """Ensure persistent session storage directories exist."""
    GOOGLE_FLOW_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    RUNNINGHUB_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    FLOWMUSIC_SESSION_DIR.mkdir(parents=True, exist_ok=True)


def is_google_flow_authenticated(page, context=None) -> bool:
    """Check if the current Google Flow page state indicates an authenticated user."""
    url = page.url.lower()
    # If redirected to Google Accounts login or signin prompt
    if "accounts.google.com" in url or "signin" in url:
        return False

    # Check context cookies first if available
    if context:
        try:
            cookies = context.cookies()
            has_sid = any(
                c.get("name") in ("SID", "__Secure-1PSID", "__Secure-3PSID", "SAPISID")
                and "google" in c.get("domain", "")
                for c in cookies
            )
            if has_sid:
                return True
        except Exception:
            pass

    # Check for authenticated indicators (e.g., flow project workspace, user profile, create prompt bar)
    try:
        # If sign-in button is present and visible, definitely NOT authenticated
        btn_signin = page.query_selector(
            'a[href*="accounts.google.com"], button:has-text("Sign in"), a:has-text("Sign in"), '
            'button:has-text("Fazer login"), a:has-text("Fazer login")'
        )
        if btn_signin and btn_signin.is_visible():
            return False

        # Profile avatar or account menu
        avatar = page.query_selector(
            'a[aria-label*="Google Account"], img[alt*="Google Account"], [aria-label*="Conta do Google"], '
            'button[aria-label*="Google Account"], [data-email]'
        )
        if avatar and avatar.is_visible():
            return True

        # Project creation or prompt interface
        prompt_box = page.query_selector(
            'textarea[placeholder*="prompt" i], textarea[placeholder*="describe" i], '
            'button:has-text("New project"), button:has-text("Create project")'
        )
        if prompt_box and prompt_box.is_visible():
            return True
    except Exception:
        pass
    return False


def is_runninghub_authenticated(page, context=None) -> bool:
    """Check if the current RunningHub page state indicates an active session."""
    url = page.url.lower()
    if "/login" in url or "/register" in url:
        return False

    # Check context cookies first
    if context:
        try:
            cookies = context.cookies()
            has_rh_token = any(
                ("runninghub" in c.get("domain", "").lower() or "rh" in c.get("name", "").lower() or c.get("domain", "") == "")
                and c.get("name") in ("token", "authorization", "auth", "session_id", "rh_token")
                for c in cookies
            )
            if has_rh_token:
                return True
        except Exception:
            pass

    try:
        # If login button is visible, definitely NOT authenticated
        btn_login = page.query_selector(
            'button:has-text("Entrar"), a:has-text("Entrar"), button:has-text("Login"), '
            'a:has-text("Login"), button:has-text("Sign in"), a:has-text("Sign in")'
        )
        if btn_login and btn_login.is_visible():
            return False

        # Check localStorage for token/user
        token_in_storage = page.evaluate(
            '() => { try { return localStorage.getItem("token") || localStorage.getItem("user") || localStorage.getItem("userInfo"); } catch(e) { return null; } }'
        )
        if token_in_storage:
            return True

        # Check for profile avatar or user menu
        user_menu = page.query_selector('.user-avatar, .avatar, [class*="avatar"], [class*="user-profile"], [class*="user-name"]')
        if user_menu and user_menu.is_visible():
            return True

        if "/workflow/" in url or "/workbench" in url:
            return True
    except Exception:
        pass
    return False


def is_flowmusic_authenticated(page, context=None) -> bool:
    """Check if the current Flow Music page state indicates an active session."""
    url = page.url.lower()
    if "signin" in url or "login" in url or "accounts.google.com" in url:
        return False

    # Check context cookies first
    if context:
        try:
            cookies = context.cookies()
            has_auth = any(
                ("flowmusic" in c.get("domain", "").lower() or "google" in c.get("domain", "").lower())
                and (
                    c.get("name") in ("SID", "__Secure-1PSID", "__Secure-3PSID", "token", "session", "auth")
                    or "token" in c.get("name", "").lower()
                    or "auth" in c.get("name", "").lower()
                )
                for c in cookies
            )
            if has_auth:
                return True
        except Exception:
            pass

    try:
        # If sign-in button is present and visible, definitely NOT authenticated
        btn_signin = page.query_selector(
            'button:has-text("Sign In"), a:has-text("Sign In"), '
            'button:has-text("Fazer Login"), a:has-text("Fazer Login"), '
            'button:has-text("Entrar"), a:has-text("Entrar")'
        )
        if btn_signin and btn_signin.is_visible():
            return False

        # Check for Compose button or audio creation workspace
        compose_btn = page.query_selector(
            'button:has-text("Compose"), button[aria-label*="compose" i], '
            'button[aria-label*="instrumental" i], textarea[aria-label*="description" i]'
        )
        if compose_btn and compose_btn.is_visible():
            return True

        # Check for user avatar or profile icon
        avatar = page.query_selector('.avatar, [class*="avatar"], [aria-label*="profile" i], [aria-label*="account" i]')
        if avatar and avatar.is_visible():
            return True
    except Exception:
        pass
    return False


def check_google_flow_session(session_dir: Optional[Path] = None, headless: bool = True, timeout_sec: int = 15) -> bool:
    """Verify whether Google Flow session is authenticated."""
    from playwright.sync_api import sync_playwright

    s_dir = session_dir or GOOGLE_FLOW_SESSION_DIR
    ensure_session_dirs()
    state_file = s_dir / "storage_state.json"
    if not (s_dir / "Default").exists() and not state_file.exists():
        logger.warning("Google Flow session directory has no saved profile or storage state.")
        return False

    # Fast verification if valid storage_state.json with Google session cookies exists
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
            cookies = state_data.get("cookies", [])
            for c in cookies:
                if c.get("name") in ("SID", "__Secure-1PSID", "__Secure-3PSID") and "google" in c.get("domain", ""):
                    return True
        except Exception:
            pass

    logger.info("Checking Google Flow session validity...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(s_dir),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.new_page() if not context.pages else context.pages[0]
            page.goto(GOOGLE_FLOW_URL, timeout=timeout_sec * 1000)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_sec * 1000)
            time.sleep(2)
            auth = is_google_flow_authenticated(page, context=context)
            context.close()
            return auth
    except Exception as exc:
        logger.warning(f"Error checking Google Flow session: {exc}")
        return False


def check_runninghub_session(session_dir: Optional[Path] = None, headless: bool = True, timeout_sec: int = 15) -> bool:
    """Verify whether RunningHub session is authenticated."""
    from playwright.sync_api import sync_playwright

    s_dir = session_dir or RUNNINGHUB_SESSION_DIR
    ensure_session_dirs()
    state_file = s_dir / "storage_state.json"
    if not (s_dir / "Default").exists() and not state_file.exists():
        logger.warning("RunningHub session directory has no saved profile or storage state.")
        return False

    # Fast verification if valid storage_state.json with RunningHub cookies exists
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
            cookies = state_data.get("cookies", [])
            for c in cookies:
                if "runninghub" in c.get("domain", "").lower() or "token" in c.get("name", "").lower():
                    return True
        except Exception:
            pass

    logger.info("Checking RunningHub session validity...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(s_dir),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.new_page() if not context.pages else context.pages[0]
            page.goto(RUNNINGHUB_URL, timeout=timeout_sec * 1000)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_sec * 1000)
            time.sleep(2)
            auth = is_runninghub_authenticated(page, context=context)
            context.close()
            return auth
    except Exception as exc:
        logger.warning(f"Error checking RunningHub session: {exc}")
        return False


def check_flowmusic_session(session_dir: Optional[Path] = None, headless: bool = True, timeout_sec: int = 15) -> bool:
    """Verify whether Flow Music session is authenticated."""
    from playwright.sync_api import sync_playwright

    s_dir = session_dir or FLOWMUSIC_SESSION_DIR
    ensure_session_dirs()
    state_file = s_dir / "storage_state.json"

    # Fast verification if valid storage_state.json exists
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
            cookies = state_data.get("cookies", [])
            for c in cookies:
                domain = c.get("domain", "").lower()
                name = c.get("name", "").lower()
                if "flowmusic" in domain or "google" in domain or "token" in name or "auth" in name or "session" in name:
                    return True
        except Exception:
            pass
    elif (s_dir / "Default").exists():
        return True

    # Check fallback: if Google Flow session exists, Flow Music shares Google SSO
    gf_state = GOOGLE_FLOW_SESSION_DIR / "storage_state.json"
    if gf_state.exists():
        try:
            gf_data = json.loads(gf_state.read_text(encoding="utf-8"))
            cookies = gf_data.get("cookies", [])
            if any(c.get("name") in ("SID", "__Secure-1PSID", "__Secure-3PSID") and "google" in c.get("domain", "") for c in cookies):
                # Copy or initialize flowmusic session with Google cookies for seamless SSO
                if not state_file.exists():
                    state_file.write_text(json.dumps(gf_data, indent=2), encoding="utf-8")
                return True
        except Exception:
            pass

    logger.info("Checking Flow Music session validity...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(s_dir),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.new_page() if not context.pages else context.pages[0]
            page.goto(FLOWMUSIC_URL, timeout=timeout_sec * 1000)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_sec * 1000)
            time.sleep(2)
            auth = is_flowmusic_authenticated(page, context=context)
            context.close()
            return auth
    except Exception as exc:
        logger.warning(f"Error checking Flow Music session: {exc}")
        return False


def interactive_login_google_flow(timeout_sec: int = 300) -> bool:
    """Launch headful browser for the operator to log into Google Flow manually."""
    from playwright.sync_api import sync_playwright

    ensure_session_dirs()
    print("\n" + "=" * 70)
    print("🔑 LOGIN INTERATIVO: GOOGLE FLOW (flow.google.com)")
    print("=" * 70)
    print("1. Uma janela visível do Chrome foi aberta.")
    print("2. Faça seu login com a conta Google diretamente no navegador.")
    print("3. Quando concluir o login, PRESSIONE [ENTER] aqui no terminal.")
    print("   (Ou aguarde a detecção automática assim que o login for concluído)")
    print("=" * 70 + "\n")

    user_confirmed = threading.Event()

    def wait_for_enter():
        try:
            input("👉 Pressione [ENTER] quando terminar de fazer login no Google Flow: ")
            user_confirmed.set()
        except Exception:
            pass

    enter_thread = threading.Thread(target=wait_for_enter, daemon=True)
    enter_thread.start()

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(GOOGLE_FLOW_SESSION_DIR),
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )
            page = context.new_page() if not context.pages else context.pages[0]
            try:
                page.goto(GOOGLE_FLOW_URL, timeout=30000)
            except Exception as e:
                logger.warning(f"Aviso ao carregar {GOOGLE_FLOW_URL}: {e}")

            start_t = time.time()
            authenticated = False

            while time.time() - start_t < timeout_sec:
                # 1. Confirmação do usuário via ENTER no terminal
                if user_confirmed.is_set():
                    logger.info("Confirmação de login recebida via terminal [ENTER]!")
                    authenticated = True
                    break

                # 2. Janela fechada manualmente pelo usuário
                all_closed = all(p_item.is_closed() for p_item in context.pages) if context.pages else False
                if all_closed:
                    logger.info("Janela do navegador foi fechada pelo usuário. Gravando sessão...")
                    authenticated = True
                    break

                # 3. Detecção automática de login
                active_page = next((p_item for p_item in context.pages if not p_item.is_closed()), None)
                if active_page:
                    try:
                        if is_google_flow_authenticated(active_page, context=context):
                            logger.info("✅ Login no Google Flow detectado automaticamente!")
                            time.sleep(3)
                            authenticated = True
                            break
                    except Exception:
                        pass

                time.sleep(2)

            if authenticated:
                state_file = GOOGLE_FLOW_SESSION_DIR / "storage_state.json"
                try:
                    context.storage_state(path=str(state_file))
                    logger.info(f"✅ Sessão persistente salva em: {state_file}")
                except Exception as e:
                    logger.warning(f"Aviso ao salvar storage_state: {e}")

                try:
                    context.close()
                except Exception:
                    pass
                return True
            else:
                logger.error(f"❌ Tempo limite ({timeout_sec}s) esgotado aguardando login no Google Flow.")
                try:
                    context.close()
                except Exception:
                    pass
                return False
    except Exception as exc:
        logger.error(f"Falha ao executar login interativo no Google Flow: {exc}")
        return False


def interactive_login_runninghub(timeout_sec: int = 300) -> bool:
    """Launch headful browser for the operator to log into RunningHub manually."""
    from playwright.sync_api import sync_playwright

    ensure_session_dirs()
    print("\n" + "=" * 70)
    print("🔑 LOGIN INTERATIVO: RUNNINGHUB (runninghub.ai)")
    print("=" * 70)
    print("1. Uma janela visível do Chrome foi aberta na página de login do RunningHub.")
    print("2. Faça seu login com suas credenciais na janela aberta.")
    print("3. Quando concluir o login, PRESSIONE [ENTER] aqui no terminal.")
    print("   (Ou aguarde a detecção automática assim que o login for concluído)")
    print("=" * 70 + "\n")

    user_confirmed = threading.Event()

    def wait_for_enter():
        try:
            input("👉 Pressione [ENTER] quando terminar de fazer login no RunningHub: ")
            user_confirmed.set()
        except Exception:
            pass

    enter_thread = threading.Thread(target=wait_for_enter, daemon=True)
    enter_thread.start()

    login_url = os.getenv("RUNNINGHUB_URL", "https://www.runninghub.ai/")

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(RUNNINGHUB_SESSION_DIR),
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )
            page = context.new_page() if not context.pages else context.pages[0]
            try:
                page.goto(login_url, timeout=30000)
            except Exception as e:
                logger.warning(f"Aviso ao carregar {login_url}: {e}")

            start_t = time.time()
            authenticated = False

            while time.time() - start_t < timeout_sec:
                # 1. Confirmação do usuário via ENTER no terminal
                if user_confirmed.is_set():
                    logger.info("Confirmação de login recebida via terminal [ENTER]!")
                    authenticated = True
                    break

                # 2. Janela fechada manualmente pelo usuário
                all_closed = all(p_item.is_closed() for p_item in context.pages) if context.pages else False
                if all_closed:
                    logger.info("Janela do navegador foi fechada pelo usuário. Gravando sessão...")
                    authenticated = True
                    break

                # 3. Detecção automática de login
                active_page = next((p_item for p_item in context.pages if not p_item.is_closed()), None)
                if active_page:
                    try:
                        if is_runninghub_authenticated(active_page, context=context):
                            logger.info("✅ Login no RunningHub detectado automaticamente!")
                            time.sleep(3)
                            authenticated = True
                            break
                    except Exception:
                        pass

                time.sleep(2)

            if authenticated:
                state_file = RUNNINGHUB_SESSION_DIR / "storage_state.json"
                try:
                    context.storage_state(path=str(state_file))
                    logger.info(f"✅ Sessão persistente salva em: {state_file}")
                except Exception as e:
                    logger.warning(f"Aviso ao salvar storage_state: {e}")

                try:
                    context.close()
                except Exception:
                    pass
                return True
            else:
                logger.error(f"❌ Tempo limite ({timeout_sec}s) esgotado aguardando login no RunningHub.")
                try:
                    context.close()
                except Exception:
                    pass
                return False
    except Exception as exc:
        logger.error(f"Falha ao executar login interativo no RunningHub: {exc}")
        return False


def interactive_login_flowmusic(timeout_sec: int = 300) -> bool:
    """Launch headful browser for the operator to log into Flow Music manually."""
    from playwright.sync_api import sync_playwright

    ensure_session_dirs()
    print("\n" + "=" * 70)
    print("🔑 LOGIN INTERATIVO: FLOW MUSIC (flowmusic.app)")
    print("=" * 70)
    print("1. Uma janela visível do Chrome foi aberta na página do Flow Music.")
    print("2. Faça seu login com a sua conta Google/credenciais no Flow Music.")
    print("3. Quando concluir o login, PRESSIONE [ENTER] aqui no terminal.")
    print("   (Ou aguarde a detecção automática assim que o login for concluído)")
    print("=" * 70 + "\n")

    user_confirmed = threading.Event()

    def wait_for_enter():
        try:
            input("👉 Pressione [ENTER] quando terminar de fazer login no Flow Music: ")
            user_confirmed.set()
        except Exception:
            pass

    enter_thread = threading.Thread(target=wait_for_enter, daemon=True)
    enter_thread.start()

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(FLOWMUSIC_SESSION_DIR),
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )

            # Preload Google Flow cookies if available for Google SSO
            gf_state = GOOGLE_FLOW_SESSION_DIR / "storage_state.json"
            if gf_state.exists():
                try:
                    gf_data = json.loads(gf_state.read_text(encoding="utf-8"))
                    cookies = gf_data.get("cookies", [])
                    if cookies:
                        context.add_cookies(cookies)
                except Exception:
                    pass

            page = context.new_page() if not context.pages else context.pages[0]
            try:
                page.goto(FLOWMUSIC_URL, timeout=30000)
            except Exception as e:
                logger.warning(f"Aviso ao carregar {FLOWMUSIC_URL}: {e}")

            start_t = time.time()
            authenticated = False

            while time.time() - start_t < timeout_sec:
                if user_confirmed.is_set():
                    logger.info("Confirmação de login recebida via terminal [ENTER]!")
                    authenticated = True
                    break

                all_closed = all(p_item.is_closed() for p_item in context.pages) if context.pages else False
                if all_closed:
                    logger.info("Janela do navegador foi fechada pelo usuário. Gravando sessão...")
                    authenticated = True
                    break

                active_page = next((p_item for p_item in context.pages if not p_item.is_closed()), None)
                if active_page:
                    try:
                        if is_flowmusic_authenticated(active_page, context=context):
                            logger.info("✅ Login no Flow Music detectado automaticamente!")
                            time.sleep(3)
                            authenticated = True
                            break
                    except Exception:
                        pass

                time.sleep(2)

            if authenticated:
                state_file = FLOWMUSIC_SESSION_DIR / "storage_state.json"
                try:
                    context.storage_state(path=str(state_file))
                    logger.info(f"✅ Sessão persistente salva em: {state_file}")
                except Exception as e:
                    logger.warning(f"Aviso ao salvar storage_state: {e}")

                try:
                    context.close()
                except Exception:
                    pass
                return True
            else:
                logger.error(f"❌ Tempo limite ({timeout_sec}s) esgotado aguardando login no Flow Music.")
                try:
                    context.close()
                except Exception:
                    pass
                return False
    except Exception as exc:
        logger.error(f"Falha ao executar login interativo no Flow Music: {exc}")
        return False


def enforce_production_auth_gate(interactive: bool = True, dry_run: bool = False) -> bool:
    """Mandatory Pre-flight gate: enforces active sessions for Google Flow and RunningHub.

    - Called by orchestrator before any asset generation begins.
    - If dry_run is True (CI/test suite), bypasses network checks.
    - If sessions are missing and interactive=True, opens headful windows automatically.
    """
    if dry_run or os.getenv("DARKFACTORY_DRY_RUN", "0") == "1":
        logger.info("🛡️ Pre-Flight Auth Gate: DRY-RUN mode active (skipping live browser sessions).")
        return True

    logger.info("🛡️ Pre-Flight Auth Gate: Verificando autenticação das plataformas industriais...")
    ensure_session_dirs()

    # 1. Google Flow Check
    flow_ok = check_google_flow_session(headless=True)
    if not flow_ok:
        logger.warning("⚠️ Sessão do Google Flow não autenticada!")
        if interactive:
            logger.info("Abrindo janela de login para Google Flow...")
            flow_ok = interactive_login_google_flow()
            if not flow_ok:
                raise PermissionError("Falha na autenticação do Google Flow. Pipeline abortado.")
        else:
            raise PermissionError("Production Auth Gate Check Failed: Google Flow não autenticado e modo interativo desativado.")

    # 2. RunningHub Check
    rh_ok = check_runninghub_session(headless=True)
    if not rh_ok:
        logger.warning("⚠️ Sessão do RunningHub não autenticada!")
        if interactive:
            logger.info("Abrindo janela de login para RunningHub...")
            rh_ok = interactive_login_runninghub()
            if not rh_ok:
                raise PermissionError("Falha na autenticação do RunningHub. Pipeline abortado.")
        else:
            raise PermissionError("Production Auth Gate Check Failed: RunningHub não autenticado e modo interativo desativado.")

    logger.info("✅ Pre-Flight Auth Gate: 100% Autenticado (Google Flow + RunningHub prontos).")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Pre-Flight Authentication Gate")
    parser.add_argument("--check", action="store_true", help="Check active session status without opening windows")
    parser.add_argument("--login-google", "--login-flow", action="store_true", help="Trigger interactive login for Google Flow")
    parser.add_argument("--login-runninghub", action="store_true", help="Trigger interactive login for RunningHub")
    parser.add_argument("--login-flowmusic", "--login-music", action="store_true", help="Trigger interactive login for Flow Music")
    parser.add_argument("--login-all", action="store_true", help="Check and trigger interactive login for all platforms")
    parser.add_argument("--dry-run", action="store_true", help="Simulate authentication gate check")
    args = parser.parse_args()

    if args.dry_run:
        ok = enforce_production_auth_gate(interactive=False, dry_run=True)
        print(f"Auth Gate Dry-Run Status: {ok}")
        sys.exit(0)

    if args.login_google:
        ok = interactive_login_google_flow()
        sys.exit(0 if ok else 1)

    if args.login_runninghub:
        ok = interactive_login_runninghub()
        sys.exit(0 if ok else 1)

    if args.login_flowmusic or getattr(args, "login_music", False):
        ok = interactive_login_flowmusic()
        sys.exit(0 if ok else 1)

    if args.login_all:
        ok_flow = interactive_login_google_flow()
        ok_rh = interactive_login_runninghub()
        ok_fm = interactive_login_flowmusic()
        sys.exit(0 if (ok_flow and ok_rh and ok_fm) else 1)

    if args.check:
        ensure_session_dirs()
        gf = check_google_flow_session(headless=True)
        rh = check_runninghub_session(headless=True)
        fm = check_flowmusic_session(headless=True)
        print(f"Google Flow Authenticated: {gf}")
        print(f"RunningHub Authenticated:  {rh}")
        print(f"Flow Music Authenticated:  {fm}")
        sys.exit(0 if (gf and rh) else 1)

    # Default action: enforce gate
    ok = enforce_production_auth_gate(interactive=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
