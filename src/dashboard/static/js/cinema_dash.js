/**
 * DarkFactory Cinema Studio — Master Frontend Orchestrator SPA
 */

let activeVideoData = null;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSSE();
  refreshAllData();

  window.cinemaVideo.init("main-cinema-video", "video-letterbox-bars", "video-subtitle-banner");

  // Periodic telemetry refresh
  setInterval(refreshTelemetry, 5000);
  setInterval(refreshAuthStatus, 5000);
});

// ── Tab Navigation ────────────────────────────────────
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-content").forEach(c => {
    c.classList.toggle("active", c.id === `tab-${tabId}`);
  });
}

// ── Real-Time SSE Log Streaming ───────────────────────
function initSSE() {
  const terminal = document.getElementById("terminal-output");
  if (!terminal) return;

  const eventSource = new EventSource("/api/stream-logs");

  eventSource.onmessage = (event) => {
    const line = document.createElement("div");
    line.className = "terminal-line";
    const text = event.data;

    if (text.includes("[ERROR]") || text.includes("[CRITICAL]")) {
      line.classList.add("error");
    } else if (text.includes("[WARN]")) {
      line.classList.add("warn");
    } else if (text.includes("[SUCCESS]")) {
      line.classList.add("success");
    } else if (text.includes("[SYSTEM]") || text.includes("[ACTION]")) {
      line.classList.add("system");
    }

    line.innerText = text;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
  };

  eventSource.onerror = () => {
    console.warn("SSE connection interrupted. Reconnecting...");
  };
}

// ── Data Refreshers ───────────────────────────────────
async function refreshAllData() {
  await Promise.all([
    refreshTelemetry(),
    refreshAuthStatus(),
    loadTopicSuggestions(),
    loadScreenplays(),
    loadVisualQueues(),
    loadAudioLibrary(),
    loadApprovalQueue(),
    loadQuarantineReports(),
  ]);
}

async function refreshTelemetry() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    const k = data.kpis;

    setText("kpi-productions", k.total_productions || 0);
    setText("kpi-completed", k.completed_episodes || 0);
    setText("kpi-pending", k.pending_approvals || 0);
    setText("kpi-greendollar", `${k.green_dollar_rate}%`);
    setText("kpi-quarantine", k.quarantined_count || 0);
    setText("kpi-scripts", k.scripts_count || 0);

    // Daemon pill
    const pill = document.getElementById("daemon-status-pill");
    const led = document.getElementById("daemon-led");
    const label = document.getElementById("daemon-status-label");
    if (pill && led && label) {
      if (k.daemon_status === "producing") {
        led.className = "pulse-led pulse-led-producing";
        label.innerText = "PRODUZINDO EPISÓDIO";
      } else if (k.daemon_status === "idle") {
        led.className = "pulse-led pulse-led-ok";
        label.innerText = "DAEMON 24/7 ONLINE";
      } else {
        led.className = "pulse-led";
        label.innerText = "SUPERVISOR OFFLINE";
      }
    }

    // Google Flow Quota bar
    const quota = k.google_flow_quota;
    if (quota) {
      setText("flow-omni-usage", `${quota.omni_used}/${quota.omni_limit}`);
      setText("flow-veo-usage", `${quota.veo_used}/${quota.veo_limit}`);
    }
  } catch (e) {
    console.warn("Error refreshing telemetry:", e);
  }
}

async function loadScreenplays() {
  try {
    const res = await fetch("/api/screenplays");
    const screenplays = await res.json();
    const container = document.getElementById("screenplays-list");
    if (!container) return;

    if (screenplays.length === 0) {
      container.innerHTML = `<div style="color:var(--label-secondary); padding:20px; text-align:center;">Nenhum roteiro sintetizado ainda. Digite um tema acima para produzir.</div>`;
      return;
    }

    const first = screenplays[0];
    setText("current-script-title", first.title);
    setText("current-script-logline", first.logline);

    // Populate timelines if available
    const tls = first.timelines || {};
    setText("thread-a-desc", tls.slow_clock || "O Relógio Lento: Gênese silenciosa, decisões secretas e falhas de engenharia ocorridas antes do colapso.");
    setText("thread-b-desc", tls.fast_clock || "O Relógio Rápido: Os 20 minutos ou 60 segundos de colapso iminente em tempo real.");
    setText("thread-c-desc", tls.aftermath || "O Pós-Impacto: Depoimentos desclassificados, testemunhos e as cicatrizes históricas.");

    // Populate alternative titles
    const titlesEl = document.getElementById("alt-titles-list");
    if (titlesEl && first.alternative_titles) {
      titlesEl.innerHTML = first.alternative_titles.map(t => `<li style="margin-bottom:6px; color:#FFE066;">${t}</li>`).join("");
    }
  } catch (e) {
    console.warn("Error loading screenplays:", e);
  }
}

async function loadVisualQueues() {
  try {
    const res = await fetch("/api/visual-queues");
    const data = await res.json();

    const veoTable = document.getElementById("veo-queue-tbody");
    if (veoTable && data.veo3_4k) {
      const items = data.veo3_4k.items || [];
      setText("veo-queue-count", `${items.length} Prompts 4K`);
      veoTable.innerHTML = items.map((item, idx) => `
        <tr>
          <td class="mono">#${idx + 1}</td>
          <td><strong style="color:var(--cinema-gold);">${item.scene_id || 'Scene'}</strong></td>
          <td>${item.prompt || item.camera_prompt || 'Cinematic 4K shot on 35mm IMAX'}</td>
          <td><span class="pill" style="border-color:#30D158; color:#30D158;">2.39:1 UHD</span></td>
        </tr>
      `).join("") || `<tr><td colspan="4" style="text-align:center; padding:16px;">Fila vazia</td></tr>`;
    }

    const omniTable = document.getElementById("omni-queue-tbody");
    if (omniTable && data.omni_flash) {
      const items = data.omni_flash.items || [];
      setText("omni-queue-count", `${items.length} Tomadas`);
      omniTable.innerHTML = items.map((item, idx) => `
        <tr>
          <td class="mono">#${idx + 1}</td>
          <td>${item.continuity_id || 'Clip'}</td>
          <td>${item.description || item.prompt || 'Continuity sequence'}</td>
          <td><span class="pill" style="border-color:#00D2FF; color:#00D2FF;">Omni 15s</span></td>
        </tr>
      `).join("") || `<tr><td colspan="4" style="text-align:center; padding:16px;">Fila vazia</td></tr>`;
    }
  } catch (e) {
    console.warn("Error loading visual queues:", e);
  }
}

async function loadAudioLibrary() {
  try {
    const res = await fetch("/api/audio-library");
    const stems = await res.json();
    window.soundLab.loadStems(stems);

    setText("voice-stem-label", stems.voice[0]?.name || "Voz (CosyVoice/Kokoro)");
    setText("ost-stem-label", stems.ost[0]?.name || "Trilha Lyria (Procedural)");
    setText("foley-stem-label", stems.foley[0]?.name || "Foley (MMAudio/Whoosh)");
    setText("master-stem-label", stems.master[0]?.name || "Master EBU R128 (-14 LUFS)");
  } catch (e) {
    console.warn("Error loading audio stems:", e);
  }
}

async function loadApprovalQueue() {
  try {
    const res = await fetch("/api/approval-queue");
    const items = await res.json();

    if (items.length === 0) {
      cleanPlayerState();
      setText("approval-empty-notice", "Nenhum documentário aguardando aprovação no momento.");
      return;
    }

    activeVideoData = items[0];
    const vid = activeVideoData;

    // Setup Video
    const videoEl = document.getElementById("main-cinema-video");
    if (videoEl && vid.url) {
      videoEl.src = vid.url;
    }

    // Subtitles
    const subSelect = document.getElementById("subtitles-selector");
    if (subSelect && vid.subtitles) {
      subSelect.innerHTML = `<option value="">Sem legendas</option>` +
        vid.subtitles.map(s => `<option value="${s.url}" data-filename="${s.filename || ''}">${s.lang.toUpperCase()} Subtitles (${s.filename || ''})</option>`).join("");
    }

    // SEO Package
    const seo = vid.seo_package || {};
    setText("seo-video-title", seo.title || vid.filename);
    setText("seo-video-desc", seo.description || "Historical documentary thriller synthesized by DarkFactory.");
    setText("seo-video-tags", (seo.tags || ["dark documentary", "history", "cold war", "imax"]).join(", "));

    // Thumbnails A/B/C
    const thumbsContainer = document.getElementById("thumbnails-grid-container");
    if (thumbsContainer && vid.thumbnails) {
      thumbsContainer.innerHTML = vid.thumbnails.map((t, idx) => `
        <div class="thumbnail-candidate ${idx === 0 ? 'selected' : ''}" data-variant="${t.variant}" onclick="cinemaVideo.selectThumbnail('${t.variant}')">
          <span class="thumb-tag">VARIANTE ${t.variant}</span>
          <img src="${t.url}" alt="${t.label}" onerror="this.src='/static/favicon.svg'">
          <div style="padding:8px; font-size:11px; color:#ddd; background:rgba(10,14,22,0.9);">
            <strong>${t.label}</strong>
            <p style="font-size:10px; color:#aaa; margin-top:3px;">${t.hypothesis}</p>
          </div>
        </div>
      `).join("");
    }

    // Green Dollar Pre-Rate
    const gd = vid.green_dollar;
    if (gd) {
      setText("gd-status", gd.status);
      setText("gd-score", `${gd.score}% GREEN DOLLAR`);
      setText("gd-suitability", gd.ad_suitability);
    }
  } catch (e) {
    console.warn("Error loading approval queue:", e);
  }
}

async function loadQuarantineReports() {
  try {
    const res = await fetch("/api/quarantine");
    const reports = await res.json();
    const container = document.getElementById("quarantine-tbody");
    if (!container) return;

    if (reports.length === 0) {
      container.innerHTML = `<tr><td colspan="3" style="text-align:center; padding:16px; color:#30D158;">Zero vídeos em quarentena. Esteira 100% em conformidade.</td></tr>`;
      return;
    }

    container.innerHTML = reports.map(r => `
      <tr>
        <td class="mono">${r.dir_name}</td>
        <td style="color:#FF453A;">${r.data?.reason || 'Reprovado por inspeção'}</td>
        <td class="mono">${r.quarantined_at.split('T')[0]}</td>
      </tr>
    `).join("");
  } catch (e) {
    console.warn("Error loading quarantine:", e);
  }
}

// ── Interactive Actions ───────────────────────────────
async function triggerNewTopic() {
  const input = document.getElementById("input-topic");
  const topic = input?.value.trim();
  if (!topic) {
    alert("Digite um tema ou incidente histórico.");
    return;
  }

  showToast(`Iniciando produção autônoma para: "${topic}"...`);
  try {
    const res = await fetch("/api/trigger-topic", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, dry_run: false })
    });
    const result = await res.json();
    if (result.status === "started") {
      switchTab("terminal");
    } else {
      alert(result.message || "Falha ao iniciar produção.");
    }
  } catch (e) {
    alert(`Erro ao conectar com API: ${e}`);
  }
}

async function triggerPhase(phaseNum) {
  showToast(`Disparando Fase ${phaseNum}...`);
  try {
    const res = await fetch("/api/run-phase", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phase: phaseNum })
    });
    const result = await res.json();
    if (result.status === "started") {
      switchTab("terminal");
    }
  } catch (e) {
    alert(`Erro ao rodar fase: ${e}`);
  }
}

async function daemonAction(action) {
  showToast(`Enviando comando '${action}' ao Daemon 24/7...`);
  try {
    const res = await fetch("/api/daemon-control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    });
    const result = await res.json();
    showToast(result.message);
    refreshTelemetry();
  } catch (e) {
    alert(`Erro ao controlar daemon: ${e}`);
  }
}

// ── 1-Click Approval Decision Actions ─────────────────
async function submitApproval(action) {
  if (!activeVideoData) {
    alert("Nenhum vídeo carregado na fila.");
    return;
  }

  let notes = null;
  if (action === "reject_quarantine") {
    notes = prompt("Motivo da rejeição para quarentena (ex: áudio recortado, artefatos no Veo):");
    if (!notes) return;
  }

  try {
    const res = await fetch("/api/approval-action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        video_id: activeVideoData.video_id,
        action: action,
        quarantine_notes: notes,
        selected_thumbnail: window.cinemaVideo.selectedThumbnailVariant
      })
    });
    const result = await res.json();
    showToast(`Decisão registrada: ${result.action || result.status}`);
    loadApprovalQueue();
    refreshTelemetry();
  } catch (e) {
    alert(`Erro na ação de aprovação: ${e}`);
  }
}

function downloadFullPackage() {
  if (!activeVideoData) {
    alert("Nenhum vídeo disponível para empacotar.");
    return;
  }
  window.open(`/api/download-package/${activeVideoData.video_id}`, "_blank");
}

// ── Asset & Episode Deletion Controls ────────────────
function cleanPlayerState() {
  activeVideoData = null;
  const videoEl = document.getElementById("main-cinema-video");
  if (videoEl) {
    videoEl.pause();
    videoEl.removeAttribute("src");
    videoEl.load();
  }
  const banner = document.getElementById("video-subtitle-banner");
  if (banner) banner.innerText = "";
  if (window.cinemaVideo) {
    window.cinemaVideo.currentSubtitles = [];
  }
  setText("seo-video-title", "—");
  setText("seo-video-desc", "—");
  setText("seo-video-tags", "—");
  const subSelect = document.getElementById("subtitles-selector");
  if (subSelect) {
    subSelect.innerHTML = '<option value="">Sem legendas</option>';
  }
  const thumbsContainer = document.getElementById("thumbnails-grid-container");
  if (thumbsContainer) {
    thumbsContainer.innerHTML = "";
  }
}

async function deleteActiveEpisode() {
  if (!activeVideoData || !activeVideoData.video_id) {
    alert("Nenhum episódio ativo na fila de aprovação.");
    return;
  }

  const vidId = activeVideoData.video_id;
  const confirmed = confirm(`Tem certeza que deseja EXCLUIR O EPISÓDIO COMPLETO "${vidId}"?\n\nEsta ação apagará permanentemente o vídeo master, legendas, pacote de algoritmo SEO e kits de disputa.`);
  if (!confirmed) return;

  showToast(`🗑️ Excluindo episódio "${vidId}"...`);
  try {
    const res = await fetch(`/api/episodes/${encodeURIComponent(vidId)}`, {
      method: "DELETE"
    });
    const result = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(result.detail || "Falha ao excluir episódio.");
    }

    showToast(`✓ Episódio "${vidId}" excluído com sucesso!`);
    cleanPlayerState();
    await loadApprovalQueue();
    await refreshTelemetry();
  } catch (e) {
    alert(`Erro ao excluir episódio: ${e.message || e}`);
  }
}

async function deleteActiveVideoAsset() {
  if (!activeVideoData || !activeVideoData.filename) {
    alert("Nenhum vídeo master ativo carregado.");
    return;
  }

  const filename = activeVideoData.filename;
  const confirmed = confirm(`Deseja excluir o arquivo de vídeo master "${filename}"?`);
  if (!confirmed) return;

  showToast(`🗑️ Excluindo vídeo master "${filename}"...`);
  try {
    const res = await fetch(`/api/asset?category=output&filename=${encodeURIComponent(filename)}`, {
      method: "DELETE"
    });
    const result = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(result.detail || "Falha ao excluir vídeo.");
    }

    showToast(`✓ Vídeo master "${filename}" excluído.`);
    const videoEl = document.getElementById("main-cinema-video");
    if (videoEl) {
      videoEl.pause();
      videoEl.removeAttribute("src");
      videoEl.load();
    }
    await loadApprovalQueue();
    await refreshTelemetry();
  } catch (e) {
    alert(`Erro ao excluir vídeo master: ${e.message || e}`);
  }
}

async function deleteActiveSubtitleAsset() {
  const subSelect = document.getElementById("subtitles-selector");
  const selectedOption = subSelect ? subSelect.options[subSelect.selectedIndex] : null;
  let filename = selectedOption?.dataset?.filename;

  if (!filename && selectedOption && selectedOption.value) {
    const parts = selectedOption.value.split("/");
    filename = parts[parts.length - 1];
  }

  if (!filename && activeVideoData?.subtitles?.length > 0) {
    filename = activeVideoData.subtitles[0].filename;
  }

  if (!filename) {
    alert("Nenhuma legenda selecionada ou disponível para exclusão.");
    return;
  }

  const confirmed = confirm(`Deseja excluir o arquivo de legenda "${filename}"?`);
  if (!confirmed) return;

  showToast(`🗑️ Excluindo legenda "${filename}"...`);
  try {
    const res = await fetch(`/api/asset?category=subtitles&filename=${encodeURIComponent(filename)}`, {
      method: "DELETE"
    });
    const result = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(result.detail || "Falha ao excluir legenda.");
    }

    showToast(`✓ Legenda "${filename}" excluída.`);
    if (window.cinemaVideo) {
      window.cinemaVideo.currentSubtitles = [];
    }
    const banner = document.getElementById("video-subtitle-banner");
    if (banner) banner.innerText = "";

    await loadApprovalQueue();
  } catch (e) {
    alert(`Erro ao excluir legenda: ${e.message || e}`);
  }
}

async function deleteActiveSeoAsset() {
  if (!activeVideoData) {
    alert("Nenhum episódio ativo na fila.");
    return;
  }

  let filename = activeVideoData.seo_filename || activeVideoData.seo_package?._filename;
  if (!filename && activeVideoData.video_id) {
    filename = `${activeVideoData.video_id}_algorithm_package.json`;
  }

  if (!filename) {
    alert("Nenhum pacote SEO identificado para exclusão.");
    return;
  }

  const confirmed = confirm(`Deseja excluir o pacote SEO "${filename}"?`);
  if (!confirmed) return;

  showToast(`🗑️ Excluindo pacote SEO "${filename}"...`);
  try {
    const res = await fetch(`/api/asset?category=seo&filename=${encodeURIComponent(filename)}`, {
      method: "DELETE"
    });
    const result = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(result.detail || "Falha ao excluir pacote SEO.");
    }

    showToast(`✓ Pacote SEO "${filename}" excluído.`);
    setText("seo-video-title", "—");
    setText("seo-video-desc", "—");
    setText("seo-video-tags", "—");
    await loadApprovalQueue();
  } catch (e) {
    alert(`Erro ao excluir pacote SEO: ${e.message || e}`);
  }
}

// ── Pipeline Reset Modal Controls ─────────────────────
function openResetModal() {
  const modal = document.getElementById("modal-reset-pipeline");
  if (modal) {
    modal.classList.add("active");
    modal.style.display = "flex";
  }
}

function closeResetModal() {
  const modal = document.getElementById("modal-reset-pipeline");
  if (modal) {
    modal.classList.remove("active");
    modal.style.display = "none";
  }
}

async function executePipelineReset() {
  const btn = document.getElementById("btn-confirm-reset");
  const includeScripts = document.getElementById("reset-include-scripts")?.checked ?? true;

  if (btn) {
    btn.disabled = true;
    btn.innerText = "Limpando esteira...";
  }

  showToast("🧹 Executando reset da esteira de testes...");
  try {
    const res = await fetch("/api/pipeline/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ include_scripts: includeScripts })
    });
    const result = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(result.detail || "Falha ao resetar esteira.");
    }

    showToast(`✓ Reset da esteira concluído com sucesso!`);
    closeResetModal();
    cleanPlayerState();
    await refreshAllData();
  } catch (e) {
    alert(`Erro ao executar reset: ${e.message || e}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerText = "🧹 Confirmar Reset Total";
    }
  }
}

// ── Sound Lab Mixer Controls ──────────────────────────
function toggleSoundLabPlayback() {
  const isPlaying = window.soundLab.togglePlayAll();
  const btn = document.getElementById("btn-soundlab-play");
  if (btn) {
    btn.innerHTML = isPlaying
      ? `<svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor"><rect x="3" y="2" width="3.5" height="12"/><rect x="9.5" y="2" width="3.5" height="12"/></svg> Pausar Mixer`
      : `<svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor"><polygon points="3,2 14,8 3,14"/></svg> Tocar 4 Stems Simultâneos`;
  }
}

function handleFaderChange(channel, sliderEl) {
  const val = parseFloat(sliderEl.value) / 100;
  window.soundLab.setVolume(channel, val);
}

function handleMute(channel, btn) {
  const isMuted = window.soundLab.toggleMute(channel);
  btn.classList.toggle("active", isMuted);
}

function handleSolo(channel, btn) {
  const isSolo = window.soundLab.toggleSolo(channel);
  btn.classList.toggle("active", isSolo);
}

// ── Video Subtitles Selection ─────────────────────────
function onSubtitleChange(selectEl) {
  const url = selectEl.value;
  if (url) {
    window.cinemaVideo.loadSubtitles(url);
  } else {
    window.cinemaVideo.currentSubtitles = [];
  }
}

// ── Helpers ───────────────────────────────────────────
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.innerText = text;
}

function showToast(msg) {
  const banner = document.getElementById("global-toast");
  if (!banner) return;
  banner.innerText = msg;
  banner.style.display = "block";
  setTimeout(() => { banner.style.display = "none"; }, 4000);
}

// ── Pre-Flight Authentication & Account Login ────────
async function refreshAuthStatus() {
  try {
    const res = await fetch("/api/auth/status");
    const data = await res.json();
    updateAuthUI(data);
  } catch (e) {
    console.warn("Error refreshing auth status:", e);
  }
}

function updateAuthUI(auth) {
  if (!auth) return;

  const flow = auth.google_flow || {};
  const rh = auth.runninghub || {};
  const allOk = auth.all_authenticated;

  // Header Pill & Button
  const headerPill = document.getElementById("auth-status-pill");
  const headerLed = document.getElementById("auth-led");
  const headerLabel = document.getElementById("auth-status-label");
  const headerBtn = document.getElementById("btn-header-login");

  if (headerPill && headerLed && headerLabel) {
    if (allOk) {
      headerLed.style.background = "#30D158";
      headerLabel.innerText = "IA SESSÕES: 100% OK";
      headerPill.style.borderColor = "rgba(48, 209, 88, 0.4)";
      if (headerBtn) {
        headerBtn.innerHTML = `<span>✓ CONTAS CONECTADAS</span>`;
        headerBtn.style.background = "rgba(48, 209, 88, 0.15)";
        headerBtn.style.color = "#30D158";
        headerBtn.style.borderColor = "rgba(48, 209, 88, 0.35)";
      }
    } else {
      headerLed.style.background = "#FF9F0A";
      headerLabel.innerText = "IA: REQUER LOGIN";
      headerPill.style.borderColor = "rgba(255, 159, 10, 0.5)";
      if (headerBtn) {
        headerBtn.innerHTML = `<svg viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M6 0a6 6 0 0 0-6 6c0 2.2 1.2 4.1 3 5.2V15l4-2 3 1V9.8A6 6 0 0 0 6 0zm0 4a2 2 0 1 1 0 4 2 2 0 0 1 0-4z"/></svg> <span>LOGAR CONTAS</span>`;
        headerBtn.className = "btn btn-sm btn-gold";
      }
    }
  }

  // Card Badges in Cockpit
  const gateBadge = document.getElementById("auth-gate-badge");
  const gateLed = document.getElementById("auth-gate-led");
  const gateText = document.getElementById("auth-gate-text");

  if (gateBadge && gateLed && gateText) {
    if (allOk) {
      gateLed.style.background = "#30D158";
      gateText.innerText = "PRE-FLIGHT GATE: LIBERADO";
      gateText.style.color = "#30D158";
      gateBadge.style.borderColor = "rgba(48, 209, 88, 0.4)";
      gateBadge.style.background = "rgba(48, 209, 88, 0.12)";
    } else {
      gateLed.style.background = "#FF9F0A";
      gateText.innerText = "PRE-FLIGHT GATE: REQUER LOGIN";
      gateText.style.color = "#FF9F0A";
      gateBadge.style.borderColor = "rgba(255, 159, 10, 0.5)";
      gateBadge.style.background = "rgba(255, 159, 10, 0.15)";
    }
  }

  // Google Flow Badge
  const flowBadge = document.getElementById("flow-auth-badge");
  if (flowBadge) {
    if (flow.authenticated) {
      flowBadge.innerText = "AUTENTICADO";
      flowBadge.style.background = "rgba(48, 209, 88, 0.2)";
      flowBadge.style.color = "#30D158";
    } else {
      flowBadge.innerText = "REQUER LOGIN";
      flowBadge.style.background = "rgba(255, 159, 10, 0.2)";
      flowBadge.style.color = "#FF9F0A";
    }
  }

  // RunningHub Badge
  const rhBadge = document.getElementById("rh-auth-badge");
  if (rhBadge) {
    if (rh.authenticated) {
      rhBadge.innerText = "AUTENTICADO";
      rhBadge.style.background = "rgba(48, 209, 88, 0.2)";
      rhBadge.style.color = "#30D158";
    } else {
      rhBadge.innerText = "REQUER LOGIN";
      rhBadge.style.background = "rgba(255, 159, 10, 0.2)";
      rhBadge.style.color = "#FF9F0A";
    }
  }

  // Flow Music Badge
  const fm = auth.flowmusic || {};
  const fmBadge = document.getElementById("flowmusic-auth-badge");
  if (fmBadge) {
    if (fm.authenticated) {
      fmBadge.innerText = "AUTENTICADO";
      fmBadge.style.background = "rgba(48, 209, 88, 0.2)";
      fmBadge.style.color = "#30D158";
    } else {
      fmBadge.innerText = "REQUER LOGIN";
      fmBadge.style.background = "rgba(255, 159, 10, 0.2)";
      fmBadge.style.color = "#FF9F0A";
    }
  }

  // Golden Standards Card: Standard 1 Badge
  const std1Badge = document.getElementById("std-1-badge");
  if (std1Badge) {
    if (allOk) {
      std1Badge.innerText = "LIBERADO";
      std1Badge.style.background = "rgba(48, 209, 88, 0.2)";
      std1Badge.style.color = "#30D158";
    } else {
      std1Badge.innerText = "REQUER LOGIN";
      std1Badge.style.background = "rgba(255, 159, 10, 0.2)";
      std1Badge.style.color = "#FF9F0A";
    }
  }
}

async function triggerAccountLogin(target = "all") {
  showToast(`🔑 Abrindo navegador para login (${target.toUpperCase()})...`);
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target: target })
    });
    const data = await res.json();
    showToast(data.message || "Janela de login aberta no desktop!");

    // Switch to Terminal tab so the operator can view real-time log stream
    switchTab("terminal");

    // Re-check auth status after brief delays
    setTimeout(refreshAuthStatus, 3000);
    setTimeout(refreshAuthStatus, 8000);
  } catch (e) {
    alert(`Erro ao iniciar login: ${e}`);
  }
}

// ── Autonomous YouTube Topic Generator (15 to 30 min) ─
let currentSelectedCategory = null;
let topicValidationTimeout = null;

async function loadTopicSuggestions(category = null) {
  const container = document.getElementById("topic-suggestions-container");
  const chipsContainer = document.getElementById("topic-category-chips");
  if (!container) return;

  currentSelectedCategory = category;

  try {
    const url = category && category !== "all" 
      ? `/api/topics/suggestions?count=4&category=${encodeURIComponent(category)}`
      : `/api/topics/suggestions?count=4`;
    
    const res = await fetch(url);
    const data = await res.json();
    const topics = data.topics || [];
    const categories = data.categories || [];

    // Render category chips
    if (chipsContainer && categories.length > 0) {
      const allActive = !category || category === "all";
      let chipsHtml = `
        <button class="badge mono" 
          style="cursor:pointer; padding:4px 10px; border-radius:6px; border:1px solid ${allActive ? '#FFD700' : 'var(--liquid-glass-border)'}; background:${allActive ? 'rgba(255,215,0,0.18)' : 'rgba(255,255,255,0.04)'}; color:${allActive ? '#FFD700' : '#A0A5B5'}; font-size:11px;"
          onclick="loadTopicSuggestions('all')">
          Todos os Temas (${categories.reduce((a, b) => a + b.count, 0)})
        </button>
      `;

      categories.forEach(cat => {
        const isActive = category === cat.id;
        chipsHtml += `
          <button class="badge mono" 
            style="cursor:pointer; padding:4px 10px; border-radius:6px; border:1px solid ${isActive ? '#FFD700' : 'var(--liquid-glass-border)'}; background:${isActive ? 'rgba(255,215,0,0.18)' : 'rgba(255,255,255,0.04)'}; color:${isActive ? '#FFD700' : '#A0A5B5'}; font-size:11px;"
            onclick="loadTopicSuggestions('${cat.id}')">
            ${cat.label} (${cat.count})
          </button>
        `;
      });
      chipsContainer.innerHTML = chipsHtml;
    }

    // Render topic suggestion cards
    if (topics.length === 0) {
      container.innerHTML = `<div style="color:var(--label-secondary); padding:15px; grid-column:1/-1; text-align:center;">Nenhum tema encontrado nesta categoria.</div>`;
      return;
    }

    container.innerHTML = topics.map(t => `
      <div style="padding:14px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; display:flex; flex-direction:column; justify-content:space-between; transition:all 0.2s ease;">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; margin-bottom:8px;">
            <span class="badge mono" style="font-size:10px; padding:2px 6px; background:rgba(0,210,255,0.12); color:#00D2FF; border-radius:4px;">
              ⏱️ ${t.duration_label}
            </span>
            <span class="badge mono" style="font-size:10px; padding:2px 6px; background:rgba(48,209,88,0.12); color:#30D158; border-radius:4px;">
              ✓ EDSA 100%
            </span>
          </div>

          <div style="font-size:10.5px; color:#FF9F0A; font-weight:700; text-transform:uppercase; margin-bottom:4px;">
            ${t.category_label}
          </div>

          <h4 style="font-size:13.5px; color:#FFF; margin:0 0 6px 0; font-weight:700; line-height:1.35;">
            ${t.title}
          </h4>

          <p style="font-size:11.5px; color:#A0A5B5; margin:0 0 10px 0; line-height:1.45;">
            ${t.viral_hook}
          </p>

          <div style="font-size:10.5px; color:#8E92A2; border-top:1px solid rgba(255,255,255,0.05); padding-top:6px; margin-bottom:12px;">
            <strong style="color:#FFD700;">3 Fios Nolan:</strong> ${t.nolan_threads?.fast_clock || 'Tensão de alta frequência'}
          </div>
        </div>

        <button class="btn btn-sm btn-gold" style="width:100%; font-weight:700; font-size:12px; padding:7px 10px;"
          onclick="selectTopic('${t.title.replace(/'/g, "\\'")}', '${t.duration_label}', '${t.category_label}')">
          👉 Usar este Tema
        </button>
      </div>
    `).join("");

  } catch (e) {
    console.warn("Error loading topic suggestions:", e);
    container.innerHTML = `<div style="color:#FF453A; padding:10px; grid-column:1/-1;">Erro ao carregar sugestões: ${e}</div>`;
  }
}

async function generateNewTopics() {
  const btn = document.getElementById("btn-generate-topics");
  if (btn) btn.innerText = "🎲 Gerando...";
  showToast("🎲 Gerando nova rodada de temas YouTube de 15 a 30 min...");
  try {
    const res = await fetch("/api/topics/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        count: 4,
        category: currentSelectedCategory && currentSelectedCategory !== "all" ? currentSelectedCategory : null
      })
    });
    const data = await res.json();
    const topics = data.topics || [];
    const container = document.getElementById("topic-suggestions-container");

    if (container && topics.length > 0) {
      container.innerHTML = topics.map(t => `
        <div style="padding:14px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; display:flex; flex-direction:column; justify-content:space-between; transition:all 0.2s ease;">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; margin-bottom:8px;">
              <span class="badge mono" style="font-size:10px; padding:2px 6px; background:rgba(0,210,255,0.12); color:#00D2FF; border-radius:4px;">
                ⏱️ ${t.duration_label}
              </span>
              <span class="badge mono" style="font-size:10px; padding:2px 6px; background:rgba(48,209,88,0.12); color:#30D158; border-radius:4px;">
                ✓ EDSA 100%
              </span>
            </div>

            <div style="font-size:10.5px; color:#FF9F0A; font-weight:700; text-transform:uppercase; margin-bottom:4px;">
              ${t.category_label}
            </div>

            <h4 style="font-size:13.5px; color:#FFF; margin:0 0 6px 0; font-weight:700; line-height:1.35;">
              ${t.title}
            </h4>

            <p style="font-size:11.5px; color:#A0A5B5; margin:0 0 10px 0; line-height:1.45;">
              ${t.viral_hook}
            </p>

            <div style="font-size:10.5px; color:#8E92A2; border-top:1px solid rgba(255,255,255,0.05); padding-top:6px; margin-bottom:12px;">
              <strong style="color:#FFD700;">3 Fios Nolan:</strong> ${t.nolan_threads?.fast_clock || 'Tensão de alta frequência'}
            </div>
          </div>

          <button class="btn btn-sm btn-gold" style="width:100%; font-weight:700; font-size:12px; padding:7px 10px;"
            onclick="selectTopic('${t.title.replace(/'/g, "\\'")}', '${t.duration_label}', '${t.category_label}')">
            👉 Usar este Tema
          </button>
        </div>
      `).join("");
      showToast("✓ Novos temas gerados e prontos para seleção!");
    }
  } catch (e) {
    alert(`Erro ao gerar temas: ${e}`);
  } finally {
    if (btn) btn.innerText = "🎲 Gerar Novos Temas";
  }
}

function selectTopic(title, durationLabel, categoryLabel) {
  const input = document.getElementById("input-topic");
  if (!input) return;

  input.value = title;
  input.focus();
  input.style.borderColor = "#FFD700";
  setTimeout(() => { input.style.borderColor = "var(--cinema-gold)"; }, 1200);

  const textEl = document.getElementById("topic-compliance-text");
  if (textEl) {
    textEl.innerHTML = `<strong>${title}</strong> (${durationLabel}) • Categoria: ${categoryLabel} • <span style="color:#30D158;">100% Green Dollar (EDSA)</span>`;
  }

  showToast(`✓ Tema selecionado: "${title}" (${durationLabel})`);
}

function onTopicInput(val) {
  clearTimeout(topicValidationTimeout);
  topicValidationTimeout = setTimeout(async () => {
    if (!val || val.trim().length < 3) return;
    try {
      const res = await fetch("/api/topics/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: val.trim() })
      });
      const data = await res.json();
      const badge = document.getElementById("topic-compliance-badge");
      const textEl = document.getElementById("topic-compliance-text");

      if (badge && textEl) {
        if (data.is_green_dollar) {
          badge.innerText = `✓ EDSA ${data.green_dollar_score}% GREEN DOLLAR`;
          badge.style.background = "rgba(48,209,88,0.15)";
          badge.style.color = "#30D158";
          textEl.innerText = "Tema histórico validado para retenção e monetização no YouTube (15 a 30 min).";
        } else {
          badge.innerText = `⚠️ ATENÇÃO (${data.green_dollar_score}%)`;
          badge.style.background = "rgba(255,159,10,0.15)";
          badge.style.color = "#FF9F0A";
          textEl.innerText = `Termos sensíveis detectados: ${data.flagged_terms.join(', ')}. Sugestão EDSA: "${data.sanitized_topic}".`;
        }
      }
    } catch (e) {
      console.warn("Validation error:", e);
    }
  }, 400);
}
