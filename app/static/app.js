// Estado Global do Front-end Top Training
const state = {
  player: "Lukas",
  level: "basico",
  targetZone: 0,
  hoveredZone: -1,
  sourceType: "video",
  sourceId: "",
  soundEnabled: true,
  homography: {
    calibrated: false,
    width_m: 8.23,
    length_m: 11.885,
    service_line_y: 5.485,
    pixel_points: [],
    reproj_error_px: 0
  },
  zones: { basico: [], medio: [], avancado: [] },
  ranking: { basico: [], medio: [], avancado: [] },
  activeRankTab: "basico",

  // Calibração no Canvas
  calibImg: null,
  calibImgW: 1920,
  calibImgH: 1080,
  calibPoints: [],
  draggingIdx: -1,
  validateMode: false,

  // Sessão de treino / vídeo analisado
  pollTimer: null,
  lastEventCount: 0,
  sessionEvents: [],
  zoneStats: [],
  totalFrames: 0,
  popupShownForSession: false,
  lastStatus: null
};

// ==================== WEB AUDIO API (FEEDBACK SONORO RF27) ====================
let audioCtx = null;
function playFeedbackBeep(isHit) {
  if (!state.soundEnabled) return;
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = isHit ? "sine" : "triangle";
    osc.frequency.setValueAtTime(isHit ? 880 : 220, audioCtx.currentTime);
    if (isHit) {
      osc.frequency.exponentialRampToValueAtTime(1320, audioCtx.currentTime + 0.14);
    } else {
      osc.frequency.exponentialRampToValueAtTime(150, audioCtx.currentTime + 0.22);
    }
    gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.24);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.25);
  } catch (e) {}
}

function toggleSound() {
  state.soundEnabled = !state.soundEnabled;
  const btn = document.getElementById("btn-sound");
  btn.textContent = state.soundEnabled ? "🔊 Som: ON" : "🔇 Som: OFF";
}

// ==================== BOTÃO SAIR DO APLICATIVO ====================
async function exitApplication() {
  if (!confirm("Deseja realmente encerrar o servidor e sair do aplicativo Top Training?")) {
    return;
  }
  if (state.pollTimer) {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
  try {
    await fetch("/api/shutdown", { method: "POST" });
  } catch (e) {}

  document.body.innerHTML = `
    <div style="width:100vw;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0b141e;color:#f0f6fc;text-align:center;padding:24px;">
      <div style="font-size:3rem;margin-bottom:12px;">🎾</div>
      <h1 style="color:#00e676;margin-bottom:8px;">Aplicativo Encerrado com Sucesso</h1>
      <p style="color:#93acc5;max-width:460px;">O servidor local do Top Training foi desligado com segurança. Você já pode fechar esta guia do navegador.</p>
    </div>
  `;
  setTimeout(() => {
    try { window.close(); } catch (e) {}
  }, 400);
}

// ==================== INICIALIZAÇÃO ====================
window.addEventListener("DOMContentLoaded", async () => {
  setupCalibrationCanvasEvents();
  setupZoneCanvasEvents();
  await fetchInitData();
  drawZoneSelectionCourt();
});

async function fetchInitData() {
  const res = await fetch("/api/init");
  const data = await res.json();

  state.homography = data.homography;
  state.zones = data.zones;
  state.ranking = data.ranking;

  // Preenche dropdown de perfis
  const profSel = document.getElementById("select-existing-profile");
  profSel.innerHTML = `<option value="">-- Novo Jogador / Digitar Abaixo --</option>`;
  data.profiles.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p;
    opt.textContent = p;
    profSel.appendChild(opt);
  });

  // Preenche dropdown de vídeos
  const vidSel = document.getElementById("select-video-file");
  vidSel.innerHTML = "";
  data.videos.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    vidSel.appendChild(opt);
  });
  if (data.videos.length > 0) {
    state.sourceId = data.videos[0];
  }

  // Preenche dropdown de câmeras
  const camSel = document.getElementById("select-camera-index");
  camSel.innerHTML = "";
  data.cameras.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = c.label;
    camSel.appendChild(opt);
  });

  updateSetupCalibBanner();
  renderRankingTable();
}

function updateSetupCalibBanner() {
  const el = document.getElementById("setup-calib-status");
  if (state.homography && state.homography.calibrated) {
    el.innerHTML = `✅ <strong>Quadra Calibrada</strong> (Erro de reprojeção: ${state.homography.reproj_error_px} px)`;
    el.style.borderColor = "#00b35f";
  } else {
    el.innerHTML = `⚠️ <strong>Quadra ainda não calibrada</strong> — Clique em "Calibrar Quadra" ou use o mapeamento padrão.`;
    el.style.borderColor = "#f5b919";
  }
}

// ==================== NAVEGAÇÃO ENTRE TELAS ====================
function switchView(viewName) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.view === viewName);
  });

  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.add("active");

  state.player = document.getElementById("input-player-name").value.trim() || "Jogador";

  if (viewName === "calibrate") {
    if (!state.calibImg) loadCalibrationSnapshot();
  } else if (viewName === "zone") {
    updateZoneSelectionLabels();
    drawZoneSelectionCourt();
  } else if (viewName === "summary") {
    drawCourt2D("summary-court-canvas", state.level, state.targetZone, -1, state.sessionEvents, state.zoneStats);
    fetch("/api/ranking").then(r => r.json()).then(rk => {
      state.ranking = rk;
      renderRankingTable();
    });
  }
}

function onSelectProfileDropdown() {
  const val = document.getElementById("select-existing-profile").value;
  if (val) {
    document.getElementById("input-player-name").value = val;
    state.player = val;
  }
}

function onSourceTypeChange() {
  const selected = document.querySelector('input[name="source_type"]:checked').value;
  state.sourceType = selected;
  document.getElementById("lbl-src-video").classList.toggle("active", selected === "video");
  document.getElementById("lbl-src-camera").classList.toggle("active", selected === "camera");
  document.getElementById("video-select-box").style.display = selected === "video" ? "block" : "none";
  document.getElementById("camera-select-box").style.display = selected === "camera" ? "block" : "none";
}

function getSelectedSourceId() {
  if (state.sourceType === "camera") {
    return document.getElementById("select-camera-index").value || "0";
  }
  return document.getElementById("select-video-file").value || "";
}

function selectLevel(lvl) {
  state.level = lvl;
  state.targetZone = 0;
  document.querySelectorAll(".level-card").forEach(c => {
    c.classList.toggle("active", c.dataset.level === lvl);
  });
}

function goToCalibration() {
  state.calibImg = null;
  switchView("calibrate");
}

// ==================== TELA 2: CALIBRAÇÃO DE 4 PONTOS E HOMOGRAFIA ====================
async function loadCalibrationSnapshot() {
  const srcId = getSelectedSourceId();
  const info = document.getElementById("calib-instruction");
  info.textContent = "Capturando imagem da fonte selecionada...";

  try {
    const res = await fetch(`/api/frame_snapshot?source_type=${state.sourceType}&source_id=${encodeURIComponent(srcId)}`);
    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || "Erro ao capturar frame.");
      return;
    }
    const data = await res.json();
    state.calibImgW = data.width;
    state.calibImgH = data.height;

    if (data.homography && data.homography.pixel_points && data.homography.pixel_points.length === 4) {
      state.calibPoints = data.homography.pixel_points.map(p => [p[0], p[1]]);
      document.getElementById("val-reproj").textContent = `${data.homography.reproj_error_px} px`;
    }

    const img = new Image();
    img.onload = () => {
      state.calibImg = img;
      const canvas = document.getElementById("calib-canvas");
      canvas.width = data.width;
      canvas.height = data.height;
      drawCalibrationCanvas();
      info.textContent = "Clique nos 4 cantos da meia quadra ou arraste qualquer ponto com o mouse.";
    };
    img.src = data.image_base64;
  } catch (e) {
    info.textContent = "Erro ao carregar frame.";
  }
}

function resetCalibrationPoints() {
  state.calibPoints = [];
  drawCalibrationCanvas();
}

function onToggleValidateMode() {
  state.validateMode = document.getElementById("chk-validate-mode").checked;
}

function setupCalibrationCanvasEvents() {
  const canvas = document.getElementById("calib-canvas");

  function getMouseImgCoords(evt) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return [
      (evt.clientX - rect.left) * scaleX,
      (evt.clientY - rect.top) * scaleY
    ];
  }

  canvas.addEventListener("mousedown", async (evt) => {
    const [mx, my] = getMouseImgCoords(evt);

    if (state.validateMode) {
      const res = await fetch("/api/validate_point", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ u: mx, v: my, level: state.level })
      });
      if (res.ok) {
        const d = await res.json();
        document.getElementById("val-px").textContent = `(${d.u}, ${d.v})`;
        document.getElementById("val-meters").textContent = `x = ${d.x_m} m, y = ${d.y_m} m`;
        document.getElementById("val-inside").textContent = d.inside_court
          ? `✅ Dentro da Meia Quadra (Zona ${d.zone_id + 1})`
          : `❌ Fora da Meia Quadra`;
      }
      return;
    }

    for (let i = 0; i < state.calibPoints.length; i++) {
      const [px, py] = state.calibPoints[i];
      if (Math.hypot(mx - px, my - py) <= 26) {
        state.draggingIdx = i;
        return;
      }
    }

    if (state.calibPoints.length < 4) {
      state.calibPoints.push([Math.round(mx), Math.round(my)]);
      drawCalibrationCanvas();
    }
  });

  canvas.addEventListener("mousemove", (evt) => {
    if (state.draggingIdx < 0) return;
    const [mx, my] = getMouseImgCoords(evt);
    state.calibPoints[state.draggingIdx] = [
      Math.max(0, Math.min(canvas.width, Math.round(mx))),
      Math.max(0, Math.min(canvas.height, Math.round(my)))
    ];
    drawCalibrationCanvas();
  });

  window.addEventListener("mouseup", () => {
    state.draggingIdx = -1;
  });
}

function drawCalibrationCanvas() {
  const canvas = document.getElementById("calib-canvas");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (state.calibImg) {
    ctx.drawImage(state.calibImg, 0, 0, canvas.width, canvas.height);
  }

  const pts = state.calibPoints;
  if (pts.length > 1) {
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) {
      ctx.lineTo(pts[i][0], pts[i][1]);
    }
    if (pts.length === 4) {
      ctx.closePath();
      ctx.fillStyle = "rgba(0, 230, 118, 0.18)";
      ctx.fill();
    }
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#00e676";
    ctx.stroke();
    ctx.restore();
  }

  const colors = ["#00e676", "#f5b919", "#00b8ff", "#ff6b81"];
  pts.forEach((p, idx) => {
    ctx.beginPath();
    ctx.arc(p[0], p[1], 12, 0, Math.PI * 2);
    ctx.fillStyle = colors[idx];
    ctx.fill();
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = "#000";
    ctx.stroke();

    ctx.fillStyle = "#000";
    ctx.font = "bold 14px Segoe UI";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(idx + 1), p[0], p[1]);
  });
}

async function saveCalibration() {
  if (state.calibPoints.length !== 4) {
    alert("Marque os 4 cantos da meia quadra antes de salvar.");
    return;
  }
  const res = await fetch("/api/calibrate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      pixel_points: state.calibPoints,
      width_m: 8.23,
      length_m: 11.885
    })
  });
  if (res.ok) {
    const data = await res.json();
    state.homography = data.homography;
    state.zones = data.zones;
    document.getElementById("val-reproj").textContent = `${state.homography.reproj_error_px} px`;
    updateSetupCalibBanner();
    alert(`Calibração salva com sucesso! Erro de reprojeção: ${state.homography.reproj_error_px} px`);
  }
}

// ==================== MAPA 2D VERTICAL DA MEIA QUADRA COM MAPA DE CALOR / DENSIDADE ====================
function getCourtRect(canvas) {
  const padX = 28;
  const padY = 26;
  return {
    x: padX,
    y: padY,
    w: canvas.width - padX * 2,
    h: canvas.height - padY * 2
  };
}

function metersToCourtCanvas(xm, ym, canvas) {
  const rect = getCourtRect(canvas);
  const W = state.homography.width_m || 8.23;
  const L = state.homography.length_m || 11.885;
  const cx = rect.x + (xm / W) * rect.w;
  const cy = rect.y + ((L - ym) / L) * rect.h;
  return [cx, cy];
}

function courtCanvasToMeters(cx, cy, canvas) {
  const rect = getCourtRect(canvas);
  const W = state.homography.width_m || 8.23;
  const L = state.homography.length_m || 11.885;
  const xm = ((cx - rect.x) / rect.w) * W;
  const ym = L - ((cy - rect.y) / rect.h) * L;
  return [xm, ym];
}

function drawCourt2D(canvasId, level, targetZone, hoveredZone, bounceEvents, zoneStats) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const rect = getCourtRect(canvas);
  const W = state.homography.width_m || 8.23;
  const L = state.homography.length_m || 11.885;
  const S = state.homography.service_line_y || 5.485;

  // Fundo externo azul claro da quadra
  ctx.fillStyle = "#3a7bb0";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Piso interno da meia quadra
  ctx.fillStyle = "#193b5c";
  ctx.fillRect(rect.x, rect.y, rect.w, rect.h);

  const statsMap = {};
  if (zoneStats && Array.isArray(zoneStats)) {
    zoneStats.forEach(zs => { statsMap[zs.id] = zs; });
  }

  const zones = state.zones[level] || [];
  zones.forEach(z => {
    const [x1, yTop] = metersToCourtCanvas(z.x1, z.y2, canvas);
    const [x2, yBot] = metersToCourtCanvas(z.x2, z.y1, canvas);
    const zw = x2 - x1;
    const zh = yBot - yTop;

    const isTarget = z.id === targetZone;
    const isHover = z.id === hoveredZone;
    const zs = statsMap[z.id];

    // Coloração de fundo + Mapa de Calor de Acertos (verde) e Erros (vermelho)
    if (zs && zs.total > 0) {
      if (zs.hits > 0) {
        const alpha = Math.min(0.55, 0.22 + zs.hits * 0.08);
        ctx.fillStyle = `rgba(0, 230, 118, ${alpha})`;
      } else {
        const alpha = Math.min(0.52, 0.18 + zs.misses * 0.08);
        ctx.fillStyle = `rgba(255, 71, 71, ${alpha})`;
      }
      ctx.fillRect(x1, yTop, zw, zh);
    } else if (isTarget) {
      ctx.fillStyle = "rgba(0, 230, 118, 0.30)";
      ctx.fillRect(x1, yTop, zw, zh);
    } else if (isHover) {
      ctx.fillStyle = "rgba(0, 230, 118, 0.18)";
      ctx.fillRect(x1, yTop, zw, zh);
    } else {
      ctx.fillStyle = "rgba(8, 18, 28, 0.42)";
      ctx.fillRect(x1, yTop, zw, zh);
    }

    // Divisórias tracejadas das zonas
    ctx.save();
    ctx.strokeStyle = isTarget ? "#00e676" : "rgba(255,255,255,0.35)";
    ctx.lineWidth = isTarget ? 2.5 : 1.2;
    ctx.setLineDash([5, 4]);
    ctx.strokeRect(x1, yTop, zw, zh);
    ctx.restore();

    // Rótulo da zona + contador de densidade de Acertos e Erros
    const midZx = x1 + zw / 2;
    const midZy = yTop + zh / 2;
    ctx.fillStyle = isTarget ? "#ffffff" : "rgba(255,255,255,0.75)";
    ctx.font = isTarget ? "bold 11px Segoe UI" : "10px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText(`Z${z.id + 1}: ${z.name}`, midZx, midZy - (zs ? 7 : 0));

    if (zs && (zs.hits > 0 || zs.misses > 0)) {
      ctx.font = "bold 10px Segoe UI";
      ctx.fillStyle = zs.hits > 0 ? "#a8ffcf" : "#ffb8b8";
      ctx.fillText(`✓${zs.hits} | ✗${zs.misses}`, midZx, midZy + 9);
    }
  });

  // Linhas oficiais brancas da meia quadra
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 2.2;
  ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);

  // Rede no topo
  ctx.beginPath();
  ctx.lineWidth = 4.5;
  ctx.moveTo(rect.x - 8, rect.y);
  ctx.lineTo(rect.x + rect.w + 8, rect.y);
  ctx.stroke();

  // Linha de saque
  const [, sy] = metersToCourtCanvas(0, S, canvas);
  ctx.beginPath();
  ctx.lineWidth = 1.8;
  ctx.moveTo(rect.x, sy);
  ctx.lineTo(rect.x + rect.w, sy);
  ctx.stroke();

  // Linha central de saque
  const [midX] = metersToCourtCanvas(W / 2, S, canvas);
  ctx.beginPath();
  ctx.moveTo(midX, rect.y);
  ctx.lineTo(midX, sy);
  ctx.stroke();

  // Desenha os quiques numerados (Verde = Acerto, Vermelho = Erro)
  if (bounceEvents && bounceEvents.length > 0) {
    bounceEvents.forEach((ev, idx) => {
      const [bx, by] = metersToCourtCanvas(ev.x_m, ev.y_m, canvas);
      const isLast = idx === bounceEvents.length - 1;

      if (isLast) {
        ctx.beginPath();
        ctx.arc(bx, by, 14, 0, Math.PI * 2);
        ctx.fillStyle = ev.is_hit ? "rgba(0, 230, 118, 0.35)" : "rgba(255, 71, 71, 0.35)";
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(bx, by, 8.5, 0, Math.PI * 2);
      ctx.fillStyle = ev.is_hit ? "#00e676" : "#ff3b30";
      ctx.fill();
      ctx.lineWidth = 1.8;
      ctx.strokeStyle = "#ffffff";
      ctx.stroke();

      ctx.fillStyle = "#000000";
      ctx.font = "bold 9px Segoe UI";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(ev.shot_number), bx, by);
    });
  }
}

// ==================== TELA 3: INTERAÇÃO DE ESCOLHA DA ZONA-FOCO ====================
function setupZoneCanvasEvents() {
  const canvas = document.getElementById("zone-canvas");

  function findZoneAtMouse(evt) {
    const rect = canvas.getBoundingClientRect();
    const cx = (evt.clientX - rect.left) * (canvas.width / rect.width);
    const cy = (evt.clientY - rect.top) * (canvas.height / rect.height);
    const [xm, ym] = courtCanvasToMeters(cx, cy, canvas);
    const zones = state.zones[state.level] || [];
    for (const z of zones) {
      if (xm >= z.x1 && xm <= z.x2 && ym >= z.y1 && ym <= z.y2) {
        return z.id;
      }
    }
    return -1;
  }

  canvas.addEventListener("mousemove", (evt) => {
    const zid = findZoneAtMouse(evt);
    if (zid !== state.hoveredZone) {
      state.hoveredZone = zid;
      drawZoneSelectionCourt();
    }
  });

  canvas.addEventListener("mouseleave", () => {
    state.hoveredZone = -1;
    drawZoneSelectionCourt();
  });

  canvas.addEventListener("click", (evt) => {
    const zid = findZoneAtMouse(evt);
    if (zid >= 0) {
      state.targetZone = zid;
      updateZoneSelectionLabels();
      drawZoneSelectionCourt();
    }
  });
}

function updateZoneSelectionLabels() {
  const levelNames = {
    basico: "Básico (2 Zonas)",
    medio: "Médio (3 Colunas)",
    avancado: "Avançado (Matriz 3x2)"
  };
  document.getElementById("zone-lbl-player").textContent = state.player;
  document.getElementById("zone-lbl-level").textContent = levelNames[state.level] || state.level;
  const zones = state.zones[state.level] || [];
  const zObj = zones.find(z => z.id === state.targetZone);
  document.getElementById("zone-lbl-target").textContent = zObj
    ? `Zona ${zObj.id + 1} — ${zObj.name}`
    : `Zona ${state.targetZone + 1}`;
}

function drawZoneSelectionCourt() {
  drawCourt2D("zone-canvas", state.level, state.targetZone, state.hoveredZone, [], []);
}

// ==================== TELA 4: ANÁLISE DE VÍDEO COMPLETO + VISUALIZAÇÃO DE QUIQUES ====================
async function startTrainingSession() {
  state.player = document.getElementById("input-player-name").value.trim() || "Jogador";
  state.sourceId = getSelectedSourceId();
  state.lastEventCount = 0;
  state.sessionEvents = [];
  state.zoneStats = [];
  state.popupShownForSession = false;

  switchView("training");

  const zones = state.zones[state.level] || [];
  const zObj = zones.find(z => z.id === state.targetZone);
  document.getElementById("trn-player").textContent = state.player;
  document.getElementById("trn-level").textContent = state.level.toUpperCase();
  document.getElementById("trn-target").textContent = zObj ? `Z${zObj.id + 1}: ${zObj.name}` : `Zona ${state.targetZone + 1}`;
  document.getElementById("live-shot-log").innerHTML = `<p class="muted">Processando...</p>`;
  document.getElementById("bounce-jump-chips").innerHTML = "";
  document.getElementById("corner-most-hits").textContent = "--";
  document.getElementById("corner-most-misses").textContent = "--";
  document.getElementById("btn-reopen-popup").style.display = "none";
  document.getElementById("btn-pause-video").textContent = "⏸️ Pausar";

  const isVideo = state.sourceType === "video";
  document.getElementById("video-stage-title").textContent = isVideo
    ? `Vídeo Analisado: ${state.sourceId}`
    : `Câmera Ao Vivo (${state.sourceId})`;
  document.getElementById("video-playback-controls").style.display = isVideo ? "flex" : "none";

  // Se for vídeo, mostra overlay enquanto analisa o vídeo como um todo
  const overlay = document.getElementById("video-analyzing-overlay");
  overlay.style.display = isVideo ? "flex" : "none";
  document.getElementById("analyzing-bar-fill").style.width = "0%";
  document.getElementById("analyzing-frame-txt").textContent = "Carregando vídeo...";

  drawCourt2D("training-court-canvas", state.level, state.targetZone, -1, [], []);

  await fetch("/api/training/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      player: state.player,
      level: state.level,
      target_zone: state.targetZone,
      source_type: state.sourceType,
      source_id: state.sourceId
    })
  });

  // Conecta stream MJPEG
  document.getElementById("live-video-feed").src = `/api/training/video_feed?t=${Date.now()}`;

  if (state.pollTimer) clearInterval(state.pollTimer);
  state.pollTimer = setInterval(pollTrainingStatus, 200);
}

async function pollTrainingStatus() {
  try {
    const res = await fetch("/api/training/status");
    const st = await res.json();
    state.lastStatus = st;
    state.totalFrames = st.total_frames || 0;

    document.getElementById("trn-status-text").textContent = st.status_msg;
    document.getElementById("live-score").textContent = st.score;
    document.getElementById("live-hits").textContent = st.hits;
    document.getElementById("live-misses").textContent = st.misses;
    document.getElementById("live-accuracy").textContent = `${st.accuracy.toFixed(1)}%`;

    if (st.most_hits_summary) {
      document.getElementById("corner-most-hits").textContent = st.most_hits_summary;
    }
    if (st.most_misses_summary) {
      document.getElementById("corner-most-misses").textContent = st.most_misses_summary;
    }

    const overlay = document.getElementById("video-analyzing-overlay");
    if (st.analyzing) {
      overlay.style.display = "flex";
      const pct = st.total_frames > 0 ? Math.min(100, Math.round((st.current_frame / st.total_frames) * 100)) : 0;
      document.getElementById("analyzing-bar-fill").style.width = `${pct}%`;
      document.getElementById("analyzing-frame-txt").textContent = `${st.status_msg}`;
      return;
    } else {
      overlay.style.display = "none";
    }

    if (st.total_frames > 0) {
      const pct = Math.min(100, Math.round((st.current_frame / st.total_frames) * 100));
      document.getElementById("trn-progress-bar").style.width = `${pct}%`;
      document.getElementById("trn-frame-counter").textContent = `Frame ${st.current_frame} / ${st.total_frames}`;
    } else {
      document.getElementById("trn-frame-counter").textContent = `Frame ao vivo #${st.current_frame}`;
    }

    // Quando o vídeo termina de ser analisado como um todo -> Dispara Popup "Vídeo Analisado"!
    if (st.source_type === "video" && st.analysis_done && !state.popupShownForSession) {
      state.popupShownForSession = true;
      state.sessionEvents = st.events || [];
      state.zoneStats = st.zone_stats || [];

      playFeedbackBeep(true);
      renderLiveShotLog(state.sessionEvents);
      renderBounceJumpChips(state.sessionEvents);
      drawCourt2D("training-court-canvas", state.level, state.targetZone, -1, state.sessionEvents, state.zoneStats);
      populateSummaryScreen(st);

      document.getElementById("btn-reopen-popup").style.display = "block";
      populateAndOpenAnalyzedPopup(st);
    }

    // No modo câmera ao vivo, atualiza conforme cada quique novo acontece
    if (st.source_type === "camera" && st.events.length > state.lastEventCount) {
      const newest = st.events[st.events.length - 1];
      playFeedbackBeep(newest.is_hit);
      state.lastEventCount = st.events.length;
      state.sessionEvents = st.events;
      state.zoneStats = st.zone_stats || [];
      renderLiveShotLog(st.events);
      drawCourt2D("training-court-canvas", state.level, state.targetZone, -1, st.events, state.zoneStats);
    }
  } catch (e) {}
}

// ==================== POPUP "VÍDEO ANALISADO" ====================
function populateAndOpenAnalyzedPopup(st) {
  document.getElementById("modal-subtitle").textContent =
    `Vídeo: ${state.sourceId} • Jogador: ${st.player} • Total de ${st.total_shots} quique(s) avaliado(s)`;
  document.getElementById("pop-score").textContent = `${st.score} pts`;
  document.getElementById("pop-hits").textContent = st.hits;
  document.getElementById("pop-misses").textContent = st.misses;
  document.getElementById("pop-accuracy").textContent = `${st.accuracy.toFixed(1)}%`;
  document.getElementById("pop-most-hits").textContent = st.most_hits_summary || "Nenhum acerto";
  document.getElementById("pop-most-misses").textContent = st.most_misses_summary || "Nenhum erro";

  const listEl = document.getElementById("pop-events-list");
  const evs = st.events || [];
  if (evs.length === 0) {
    listEl.innerHTML = `<p class="muted">Nenhum quique de bola em movimento foi detectado neste vídeo.</p>`;
  } else {
    listEl.innerHTML = evs
      .map(e => `
        <div class="shot-item ${e.is_hit ? 'hit' : 'miss'}" onclick="jumpToBounceFromPopup(${e.frame})">
          <div>
            <strong>Quique #${e.shot_number}</strong> &bull; Tempo: <strong>${e.time_sec}s</strong> (Frame ${e.frame})
            <br/>
            <span class="muted">Quadra: (${e.x_m}m, ${e.y_m}m) &rarr; ${e.zone_name || ('Zona ' + (e.zone_id + 1))}</span>
          </div>
          <div style="text-align:right;">
            <strong style="color:${e.is_hit ? 'var(--accent-green)' : 'var(--accent-red)'};">
              ${e.is_hit ? '✅ ACERTO (+10)' : '❌ ERRO (-5)'}
            </strong>
            <br/>
            <small style="color:#93acc5;text-decoration:underline;">▶️ Ver no vídeo</small>
          </div>
        </div>
      `)
      .join("");
  }

  document.getElementById("modal-video-analyzed").style.display = "flex";
}

function openAnalyzedPopup() {
  if (state.lastStatus) {
    populateAndOpenAnalyzedPopup(state.lastStatus);
  } else {
    document.getElementById("modal-video-analyzed").style.display = "flex";
  }
}

function closeAnalyzedPopup() {
  document.getElementById("modal-video-analyzed").style.display = "none";
}

function jumpToBounceFromPopup(frameIdx) {
  closeAnalyzedPopup();
  seekVideoToFrame(Math.max(0, frameIdx - 25));
}

// ==================== CONTROLES DE REPRODUÇÃO E ATALHOS DE QUIQUES ====================
function renderBounceJumpChips(events) {
  const wrap = document.getElementById("bounce-jump-chips");
  if (!events || events.length === 0) {
    wrap.innerHTML = `<span class="muted">Nenhum quique detectado neste vídeo.</span>`;
    return;
  }
  wrap.innerHTML = `<span class="muted" style="align-self:center;margin-right:4px;">Ir para Quique:</span>` +
    events.map(e => `
      <button class="bounce-chip ${e.is_hit ? 'hit' : 'miss'}" onclick="seekVideoToFrame(${Math.max(0, e.frame - 25)})" title="Clique para ver o Quique #${e.shot_number} no vídeo">
        🎯 #${e.shot_number} (${e.time_sec}s) ${e.is_hit ? '✓' : '✗'}
      </button>
    `).join("");
}

function renderLiveShotLog(events) {
  const container = document.getElementById("live-shot-log");
  if (!events || events.length === 0) {
    container.innerHTML = `<p class="muted">Nenhum quique contabilizado.</p>`;
    return;
  }
  container.innerHTML = events
    .map(e => `
      <div class="shot-item ${e.is_hit ? 'hit' : 'miss'}" onclick="seekVideoToFrame(${Math.max(0, e.frame - 25)})" title="Clique para ver este quique no vídeo">
        <span><strong>#${e.shot_number}</strong> (${e.time_sec}s) &bull; Z${e.zone_id + 1}</span>
        <strong>${e.is_hit ? '+10' : '-5'}</strong>
      </div>
    `)
    .join("");
}

async function toggleVideoPause() {
  const res = await fetch("/api/training/video_control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "toggle_pause" })
  });
  if (res.ok) {
    const data = await res.json();
    document.getElementById("btn-pause-video").textContent = data.paused ? "▶️ Reproduzir" : "⏸️ Pausar";
  }
}

async function restartVideoReplay() {
  await fetch("/api/training/video_control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "restart" })
  });
  document.getElementById("btn-pause-video").textContent = "⏸️ Pausar";
}

async function seekVideoToFrame(frameIdx) {
  await fetch("/api/training/video_control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "seek", frame: frameIdx })
  });
}

function onSeekBarClick(evt) {
  if (!state.totalFrames || state.totalFrames <= 0) return;
  const bar = document.getElementById("video-seek-bar");
  const rect = bar.getBoundingClientRect();
  const ratio = Math.max(0, Math.min(1, (evt.clientX - rect.left) / rect.width));
  const targetFrame = Math.floor(ratio * state.totalFrames);
  seekVideoToFrame(targetFrame);
}

async function stopTrainingSession() {
  await fetch("/api/training/stop", { method: "POST" });
}

async function finishAndGoToSummary() {
  await stopTrainingSession();
  if (state.pollTimer) {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
  if (state.lastStatus) {
    populateSummaryScreen(state.lastStatus);
  }
  switchView("summary");
}

async function changeDifficultyDuringTraining() {
  await stopTrainingSession();
  if (state.pollTimer) clearInterval(state.pollTimer);
  switchView("zone");
}

async function changeProfileDuringTraining() {
  await stopTrainingSession();
  if (state.pollTimer) clearInterval(state.pollTimer);
  switchView("setup");
}

// ==================== TELA 5: RESUMO DA SESSÃO & RANKING ====================
function populateSummaryScreen(st) {
  document.getElementById("sum-score").textContent = st.score;
  document.getElementById("sum-hits").textContent = st.hits;
  document.getElementById("sum-misses").textContent = st.misses;
  document.getElementById("sum-accuracy").textContent = `${st.accuracy.toFixed(1)}%`;
  state.activeRankTab = state.level;
  switchRankingTab(state.level);
}

function switchRankingTab(lvl) {
  state.activeRankTab = lvl;
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.rankLevel === lvl);
  });
  renderRankingTable();
}

function renderRankingTable() {
  const tbody = document.getElementById("ranking-tbody");
  const rows = (state.ranking && state.ranking[state.activeRankTab]) || [];
  if (rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="muted">Nenhum treino registrado neste nível ainda.</td></tr>`;
    return;
  }
  tbody.innerHTML = rows
    .map((r, i) => `
      <tr>
        <td><strong>${i + 1}º</strong></td>
        <td><strong>${r.player}</strong></td>
        <td><strong class="highlight-green">${r.score} pts</strong></td>
        <td>${r.hits}</td>
        <td>${r.misses}</td>
        <td>${r.accuracy.toFixed(1)}%</td>
        <td>${r.date}</td>
      </tr>
    `)
    .join("");
}
