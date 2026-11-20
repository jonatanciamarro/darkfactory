#!/usr/bin/env python3
"""Dedicated interactive Google Flow login with robust state detection."""
import logging
from pathlib import Path
import sys
import time
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LoginGoogleFlow")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SESSION_DIR = PROJECT_ROOT / "chrome_session" / "google_flow"
STATE_FILE = SESSION_DIR / "storage_state.json"

print("\n" + "=" * 70)
print("🔑 DARKFACTORY — LOGIN INTERATIVO GOOGLE FLOW")
print("=" * 70)
print("1. A janela do navegador será aberta na sua tela.")
print("2. Faça o login na sua conta Google.")
print("3. Assim que o Google Flow abrir logado, o sistema salvará a sessão.")
print("   (Você também pode fechar o navegador quando terminar o login!)")
print("=" * 70 + "\n")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    login_url = "https://accounts.google.com/v3/signin/accountchooser?continue=https://flow.google.com/&flowName=WebLiteSignIn&flowEntry=ServiceLogin"
    logger.info(f"Abrindo tela de login: {login_url}")
    page.goto(login_url)

    start_time = time.time()
    max_wait_sec = 300  # 5 minutos
    success = False

    while time.time() - start_time < max_wait_sec:
        # Se usuário fechou a janela
        if not ctx.pages or all(p_item.is_closed() for p_item in ctx.pages):
            logger.info("Janela do navegador foi fechada pelo operador. Salvando cookies...")
            success = True
            break

        active_page = next((p_item for p_item in ctx.pages if not p_item.is_closed()), None)
        if active_page:
            curr_url = active_page.url.lower()
            
            # Se ainda estiver na tela de login da Google, aguarda o usuário
            if "accounts.google.com" in curr_url or "signin" in curr_url:
                pass
            elif "flow.google.com" in curr_url:
                # Checar se não é a landing page com o botão Create
                try:
                    landing_btn = active_page.query_selector('button:has-text("Create with Google Flow")')
                    if landing_btn and landing_btn.is_visible():
                        pass  # Ainda na landing page
                    else:
                        # Logado com sucesso no Flow!
                        logger.info(f"🎉 Login detectado com sucesso no Flow! URL: {active_page.url}")
                        time.sleep(3)
                        ctx.storage_state(path=str(STATE_FILE))
                        logger.info(f"✅ Sessão persistente salva em: {STATE_FILE}")
                        success = True
                        break
                except Exception:
                    pass

        time.sleep(2)

    try:
        ctx.storage_state(path=str(STATE_FILE))
        logger.info(f"Sessão gravada com sucesso em: {STATE_FILE}")
    except Exception as e:
        logger.warning(f"Aviso ao salvar sessão: {e}")

    ctx.close()
    if success:
        print("\n✅ LOGIN CONCLUÍDO E SALVO COM SUCESSO!\n")
    else:
        print("\n⚠️ Tempo limite atingido sem confirmação de login.\n")
