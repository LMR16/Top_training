// Estado Global — Top Training (Stealth Dark Minimal)
const state = {
  currentView: "profile",
  player: "Lukas",
  profiles: [],
  profilesMeta: {},
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

// ==================== WEB AUDIO API (FEEDBACK SONORO) ====================
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
    gain.gain.setValueAtTime(0.16, audioCtx.currentTime);
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
  if (btn) {
    btn.textContent = state.soundEnabled ? "Som: ON" : "Som: OFF";
  }
}

// ==================== BOTÃO SAIR DO APLICATIVO ====================
async function exitApplication() {
  if (!confirm("Deseja encerrar o aplicativo Top Training?")) {
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
    <div style="width:100vw;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#09090b;color:#fafafa;text-align:center;padding:24px;font-family:Inter,sans-serif;">
      <div style="width:12px;height:12px;border-radius:50%;background:#10b981;margin-bottom:18px;box-shadow:0 0 16px #10b981;"></div>
      <h2 style="font-weight:700;margin-bottom:8px;">Sessão Encerrada</h2>
      <p style="color:#a1a1aa;font-size:0.9rem;max-width:380px;">O servidor local foi desligado com segurança. Você já pode fechar esta guia.</p>
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
  switchView("profile");
});

async function fetchInitData() {
  const res = await fetch("/api/init");
  const data = await res.json();

  state.profiles = data.profiles || [];
  state.profilesMeta = data.profiles_meta || {};
  state.homography = data.homography;
  state.zones = data.zones;
  state.ranking = data.ranking;

  renderProfileSelectionUI();

  // Preenche dropdown de vídeos
  const vidSel = document.getElementById("select-video-file");
  if (vidSel) {
    vidSel.innerHTML = "";
    (data.videos || []).forEach(v => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      vidSel.appendChild(opt);
    });
    if (data.videos && data.videos.length > 0) {
      state.sourceId = data.videos[0];
    }
  }

  // Preenche dropdown de câmeras
  const camSel = document.getElementById("select-camera-index");
  if (camSel) {
    camSel.innerHTML = "";
    (data.cameras || []).forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.label;
      camSel.appendChild(opt);
    });
  }

  updateHubCalibrationBadge();
  renderRankingTable();
}

function renderProfileSelectionUI() {
  const chipsWrap = document.getElementById("profile-chips-list");
  const section = document.getElementById("existing-profiles-section");
  const profSel = document.getElementById("select-existing-profile");

  if (!state.profiles || state.profiles.length === 0) {
    if (section) section.style.display = "none";
    return;
  }

  if (section) section.style.display = "flex";

  if (chipsWrap) {
    chipsWrap.innerHTML = state.profiles
      .map(p => {
        const isCurrent = p.toLowerCase() === (state.player || "").toLowerCase();
        return `<button type="button" class="profile-chip ${isCurrent ? 'active' : ''}" onclick="selectProfileChip('${p.replace(/'/g, "\\'")}')">${p}</button>`;
      })
      .join("");
  }

  if (profSel) {
    profSel.innerHTML = `<option value="">Novo jogador</option>`;
    state.profiles.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      profSel.appendChild(opt);
    });
  }
}

function selectProfileChip(name) {
  state.player = name;
  const input = document.getElementById("input-player-name");
  if (input) input.value = name;
  renderProfileSelectionUI();
}

function onSelectProfileDropdown() {
  const val = document.getElementById("select-existing-profile").value;
  if (val) {
    selectProfileChip(val);
  }
}

async function confirmProfileAndEnterHub() {
  const input = document.getElementById("input-player-name");
  const cleanName = (input && input.value.trim()) ? input.value.trim() : "Jogador";
  state.player = cleanName;

  try {
    const res = await fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: cleanName })
    });
    if (res.ok) {
      const d = await res.json();
      state.player = d.player;
      state.profiles = d.profiles || state.profiles;
      state.profilesMeta = d.profiles_meta || state.profilesMeta;
      renderProfileSelectionUI();
    }
  } catch (e) {}

  updateHubView();
  switchView("hub");
}

function updateHubView() {
  const titleEl = document.getElementById("hub-title-player");
  const hudName = document.getElementById("hud-player-name");
  const sessEl = document.getElementById("hub-stat-sessions");
  const bestEl = document.getElementById("hub-stat-best");

  if (titleEl) titleEl.textContent = state.player;
  if (hudName) hudName.textContent = state.player;

  const meta = state.profilesMeta[state.player] || { sessions_count: 0, best_score: 0 };
  if (sessEl) sessEl.textContent = meta.sessions_count;
  if (bestEl) bestEl.textContent = `${meta.best_score} pts`;

  updateHubCalibrationBadge();
}

function updateHubCalibrationBadge() {
  const badge = document.getElementById("hub-calib-badge");
  if (!badge) return;
  if (state.homography && state.homography.calibrated) {
    badge.textContent = "Calibrada";
    badge.className = "status-tag ok";
  } else {
    badge.textContent = "Padrão";
    badge.className = "status-tag pending";
  }
}

// ==================== NAVEGAÇÃO FLUIDA DE FOCO ÚNICO ====================
function switchView(viewName) {
  state.currentView = viewName;
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));

  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.add("active");

  // Fundo: Vivo no início/hub, escurecido (93%) nas telas de quadra/vídeo
  const vividViews = ["profile", "hub"];
  document.body.classList.toggle("bg-vivid", vividViews.includes(viewName));
  document.body.classList.toggle("bg-dimmed", !vividViews.includes(viewName));

  // Controles de canto
  const backBtn = document.getElementById("btn-global-back");
  const playerPill = document.getElementById("hud-player-pill");
  if (backBtn) {
    backBtn.style.display = viewName === "profile" ? "none" : "inline-flex";
  }
  if (playerPill) {
    playerPill.style.display = viewName === "profile" ? "none" : "inline-flex";
    document.getElementById("hud-player-name").textContent = state.player;
  }

  if (viewName === "hub") {
    fetch("/api/init").then(r => r.json()).then(d => {
      state.profilesMeta = d.profiles_meta || {};
      state.homography = d.homography || state.homography;
      updateHubView();
    }).catch(() => {});
  } else if (viewName === "calibrate") {
    if (!state.calibImg) loadCalibrationSnapshot();
  } else if (viewName === "zone") {
    updateZoneSelectionLabels();
    drawZoneSelectionCourt();
  } else if (viewName === "summary") {
    drawCourt2D("summary-court-canvas", state.level, state.targetZone, -1, state.sessionEvents, state.zoneStats);
    fetch("/api/ranking").then(r => r.json()).then(rk => {
      state.ranking = rk;
      renderRankingTable();
    }).catch(() => {});
  }
}

async function navigateBack() {
  if (state.currentView === "training") {
    await stopTrainingSession();
    if (state.pollTimer) {
      clearInterval(state.pollTimer);
      state.pollTimer = null;
    }
    switchView("zone");
  } else if (state.currentView === "zone" || state.currentView === "calibrate" || state.currentView === "summary") {
    switchView("hub");
  } else if (state.currentView === "hub") {
    switchView("profile");
  }
}

function setSourceType(type) {
  state.sourceType = type;
  const btnVid = document.getElementById("seg-src-video");
  const btnCam = document.getElementById("seg-src-camera");
  if (btnVid) btnVid.classList.toggle("active", type === "video");
  if (btnCam) btnCam.classList.toggle("active", type === "camera");

  const vidBox = document.getElementById("video-select-box");
  const camBox = document.getElementById("camera-select-box");
  if (vidBox) vidBox.style.display = type === "video" ? "block" : "none";
  if (camBox) camBox.style.display = type === "camera" ? "block" : "none";
}

function getSelectedSourceId() {
  if (state.sourceType === "camera") {
    const el = document.getElementById("select-camera-index");
    return (el && el.value) ? el.value : "0";
  }
  const el = document.getElementById("select-video-file");
  return (el && el.value) ? el.value : "";
}

function selectLevel(lvl) {
  state.level = lvl;
  state.targetZone = 0;
  document.querySelectorAll(".level-pill").forEach(c => {
    c.classList.toggle("active", c.dataset.level === lvl);
  });
  updateZoneSelectionLabels();
  drawZoneSelectionCourt();
}

function goToCalibration() {
  state.calibImg = null;
  switchView("calibrate");
}

// ==================== CALIBRAÇÃO DE 4 PONTOS E HOMOGRAFIA ====================
async function loadCalibrationSnapshot() {
  const srcId = getSelectedSourceId();
  const info = document.getElementById("calib-instruction");
  if (info) info.textContent = "Capturando frame...";

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
      if (info) info.textContent = "Clique ou arraste os 4 cantos da meia quadra oposta.";
    };
    img.src = data.image_base64;
  } catch (e) {
    if (info) info.textContent = "Erro ao carregar frame.";
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
  if (!canvas) return;

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
        document.getElementById("val-meters").textContent = `${d.x_m}m, ${d.y_m}m`;
        document.getElementById("val-inside").textContent = d.inside_court
          ? `Dentro (Z${d.zone_id + 1})`
          : `Fora`;
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
  if (!canvas) return;
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
      ctx.fillStyle = "rgba(16, 185, 129, 0.18)";
      ctx.fill();
    }
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = "#10b981";
    ctx.stroke();
    ctx.restore();
  }

  const colors = ["#10b981", "#f59e0b", "#38bdf8", "#f43f5e"];
  pts.forEach((p, idx) => {
    ctx.beginPath();
    ctx.arc(p[0], p[1], 11, 0, Math.PI * 2);
    ctx.fillStyle = colors[idx];
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#09090b";
    ctx.stroke();

    ctx.fillStyle = "#09090b";
    ctx.font = "bold 13px Inter, sans-serif";
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
    updateHubCalibrationBadge();
  }
}

// ==================== QUADRA 2D MINIMALISTA E MAPA DE CALOR ====================
function getCourtRect(canvas) {
  const padX = 24;
  const padY = 22;
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

  // Fundo externo Stealth Dark
  ctx.fillStyle = "#0d1017";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Superfície interna da meia quadra
  ctx.fillStyle = "#131c29";
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

    if (zs && zs.total > 0) {
      if (zs.hits > 0) {
        const alpha = Math.min(0.5, 0.2 + zs.hits * 0.08);
        ctx.fillStyle = `rgba(16, 185, 129, ${alpha})`;
      } else {
        const alpha = Math.min(0.45, 0.16 + zs.misses * 0.08);
        ctx.fillStyle = `rgba(239, 68, 68, ${alpha})`;
      }
      ctx.fillRect(x1, yTop, zw, zh);
    } else if (isTarget) {
      ctx.fillStyle = "rgba(16, 185, 129, 0.24)";
      ctx.fillRect(x1, yTop, zw, zh);
    } else if (isHover) {
      ctx.fillStyle = "rgba(16, 185, 129, 0.12)";
      ctx.fillRect(x1, yTop, zw, zh);
    }

    // Divisórias das zonas
    ctx.save();
    ctx.strokeStyle = isTarget ? "#10b981" : "rgba(255, 255, 255, 0.14)";
    ctx.lineWidth = isTarget ? 2 : 1;
    ctx.setLineDash([4, 4]);
    ctx.strokeRect(x1, yTop, zw, zh);
    ctx.restore();

    // Rótulo minimalista
    const midZx = x1 + zw / 2;
    const midZy = yTop + zh / 2;
    ctx.fillStyle = isTarget ? "#fafafa" : "rgba(255, 255, 255, 0.55)";
    ctx.font = isTarget ? "600 11px Inter, sans-serif" : "500 10px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(z.name, midZx, midZy - (zs ? 6 : 0));

    if (zs && (zs.hits > 0 || zs.misses > 0)) {
      ctx.font = "600 10px Inter, sans-serif";
      ctx.fillStyle = zs.hits > 0 ? "#34d399" : "#f87171";
      ctx.fillText(`✓${zs.hits}  ✗${zs.misses}`, midZx, midZy + 9);
    }
  });

  // Linhas oficiais da quadra
  ctx.strokeStyle = "rgba(255, 255, 255, 0.78)";
  ctx.lineWidth = 1.8;
  ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);

  // Rede no topo
  ctx.beginPath();
  ctx.strokeStyle = "#10b981";
  ctx.lineWidth = 3.5;
  ctx.moveTo(rect.x - 6, rect.y);
  ctx.lineTo(rect.x + rect.w + 6, rect.y);
  ctx.stroke();

  // Linha de saque e linha central
  ctx.strokeStyle = "rgba(255, 255, 255, 0.55)";
  ctx.lineWidth = 1.4;
  const [, sy] = metersToCourtCanvas(0, S, canvas);
  ctx.beginPath();
  ctx.moveTo(rect.x, sy);
  ctx.lineTo(rect.x + rect.w, sy);
  ctx.stroke();

  const [midX] = metersToCourtCanvas(W / 2, S, canvas);
  ctx.beginPath();
  ctx.moveTo(midX, rect.y);
  ctx.lineTo(midX, sy);
  ctx.stroke();

  // Quiques numerados
  if (bounceEvents && bounceEvents.length > 0) {
    bounceEvents.forEach((ev, idx) => {
      const [bx, by] = metersToCourtCanvas(ev.x_m, ev.y_m, canvas);
      const isLast = idx === bounceEvents.length - 1;

      if (isLast) {
        ctx.beginPath();
        ctx.arc(bx, by, 13, 0, Math.PI * 2);
        ctx.fillStyle = ev.is_hit ? "rgba(16, 185, 129, 0.32)" : "rgba(239, 68, 68, 0.32)";
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(bx, by, 8, 0, Math.PI * 2);
      ctx.fillStyle = ev.is_hit ? "#10b981" : "#ef4444";
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = "#09090b";
      ctx.stroke();

      ctx.fillStyle = "#09090b";
      ctx.font = "bold 9px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(ev.shot_number), bx, by);
    });
  }
}

// ==================== INTERAÇÃO NA QUADRA 2D (ESCOLHA DE ZONA) ====================
function setupZoneCanvasEvents() {
  const canvas = document.getElementById("zone-canvas");
  if (!canvas) return;

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
  const zones = state.zones[state.level] || [];
  const zObj = zones.find(z => z.id === state.targetZone);
  const targetEl = document.getElementById("zone-lbl-target");
  if (targetEl) {
    targetEl.textContent = zObj
      ? `${zObj.name}`
      : `Zona ${state.targetZone + 1}`;
  }
}

function drawZoneSelectionCourt() {
  drawCourt2D("zone-canvas", state.level, state.targetZone, state.hoveredZone, [], []);
}

// ==================== SESSÃO DE VÍDEO / TREINO ====================
async function startTrainingSession() {
  state.sourceId = getSelectedSourceId();
  state.lastEventCount = 0;
  state.sessionEvents = [];
  state.zoneStats = [];
  state.popupShownForSession = false;

  switchView("training");

  document.getElementById("bounce-jump-chips").innerHTML = "";
  document.getElementById("corner-most-hits").textContent = "--";
  document.getElementById("corner-most-misses").textContent = "--";
  document.getElementById("btn-reopen-popup").style.display = "none";
  document.getElementById("btn-pause-video").textContent = "Pausar";

  const isVideo = state.sourceType === "video";
  document.getElementById("video-playback-controls").style.display = isVideo ? "flex" : "none";

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

    document.getElementById("live-score").textContent = st.score;
    document.getElementById("live-hits").textContent = st.hits;
    document.getElementById("live-misses").textContent = st.misses;
    document.getElementById("live-accuracy").textContent = `${st.accuracy.toFixed(0)}%`;

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
      document.getElementById("analyzing-frame-txt").textContent = st.status_msg;
      return;
    } else {
      overlay.style.display = "none";
    }

    if (st.total_frames > 0) {
      const pct = Math.min(100, Math.round((st.current_frame / st.total_frames) * 100));
      document.getElementById("trn-progress-bar").style.width = `${pct}%`;
      document.getElementById("trn-frame-counter").textContent = `${st.current_frame} / ${st.total_frames}`;
    } else {
      document.getElementById("trn-frame-counter").textContent = `#${st.current_frame}`;
    }

    if (st.source_type === "video" && st.analysis_done && !state.popupShownForSession) {
      state.popupShownForSession = true;
      state.sessionEvents = st.events || [];
      state.zoneStats = st.zone_stats || [];

      playFeedbackBeep(true);
      renderBounceJumpChips(state.sessionEvents);
      drawCourt2D("training-court-canvas", state.level, state.targetZone, -1, state.sessionEvents, state.zoneStats);
      populateSummaryScreen(st);

      document.getElementById("btn-reopen-popup").style.display = "block";
      populateAndOpenAnalyzedPopup(st);
    }

    if (st.source_type === "camera" && st.events.length > state.lastEventCount) {
      const newest = st.events[st.events.length - 1];
      playFeedbackBeep(newest.is_hit);
      state.lastEventCount = st.events.length;
      state.sessionEvents = st.events;
      state.zoneStats = st.zone_stats || [];
      drawCourt2D("training-court-canvas", state.level, state.targetZone, -1, st.events, state.zoneStats);
    }
  } catch (e) {}
}

// ==================== POPUP "VÍDEO ANALISADO" ====================
function populateAndOpenAnalyzedPopup(st) {
  document.getElementById("modal-subtitle").textContent =
    `${state.sourceId} • ${st.total_shots} quique(s) detectado(s)`;
  document.getElementById("pop-score").textContent = st.score;
  document.getElementById("pop-hits").textContent = st.hits;
  document.getElementById("pop-misses").textContent = st.misses;
  document.getElementById("pop-accuracy").textContent = `${st.accuracy.toFixed(0)}%`;
  document.getElementById("pop-most-hits").textContent = st.most_hits_summary || "Nenhum";
  document.getElementById("pop-most-misses").textContent = st.most_misses_summary || "Nenhum";

  const listEl = document.getElementById("pop-events-list");
  const evs = st.events || [];
  if (evs.length === 0) {
    listEl.innerHTML = `<p class="subtle">Nenhum quique detectado neste vídeo.</p>`;
  } else {
    listEl.innerHTML = evs
      .map(e => `
        <div class="shot-item ${e.is_hit ? 'hit' : 'miss'}" onclick="jumpToBounceFromPopup(${e.frame})">
          <div>
            <strong>#${e.shot_number}</strong> &bull; ${e.time_sec}s
            <span class="subtle" style="margin-left:6px;">${e.zone_name || ('Zona ' + (e.zone_id + 1))}</span>
          </div>
          <div>
            <strong class="${e.is_hit ? 'text-emerald' : 'text-danger'}">
              ${e.is_hit ? '+10 pts' : '-5 pts'}
            </strong>
            <span class="subtle" style="margin-left:8px;font-size:0.74rem;">Ver &rarr;</span>
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

// ==================== CONTROLES DE REPRODUÇÃO E CHIPS DE QUIQUES ====================
function renderBounceJumpChips(events) {
  const wrap = document.getElementById("bounce-jump-chips");
  if (!wrap) return;
  if (!events || events.length === 0) {
    wrap.innerHTML = `<span class="subtle" style="font-size:0.75rem;">Nenhum quique detectado.</span>`;
    return;
  }
  wrap.innerHTML = events.map(e => `
    <button class="bounce-chip ${e.is_hit ? 'hit' : 'miss'}" onclick="seekVideoToFrame(${Math.max(0, e.frame - 25)})">
      #${e.shot_number} (${e.time_sec}s) ${e.is_hit ? '✓' : '✗'}
    </button>
  `).join("");
}

async function toggleVideoPause() {
  const res = await fetch("/api/training/video_control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "toggle_pause" })
  });
  if (res.ok) {
    const data = await res.json();
    document.getElementById("btn-pause-video").textContent = data.paused ? "Continuar" : "Pausar";
  }
}

async function restartVideoReplay() {
  await fetch("/api/training/video_control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "restart" })
  });
  document.getElementById("btn-pause-video").textContent = "Pausar";
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

// ==================== RANKING & RESUMO ====================
function populateSummaryScreen(st) {
  document.getElementById("sum-score").textContent = st.score;
  document.getElementById("sum-hits").textContent = st.hits;
  document.getElementById("sum-misses").textContent = st.misses;
  document.getElementById("sum-accuracy").textContent = `${st.accuracy.toFixed(0)}%`;
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
  if (!tbody) return;
  const rows = (state.ranking && state.ranking[state.activeRankTab]) || [];
  if (rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="subtle">Nenhum treino registrado neste nível.</td></tr>`;
    return;
  }
  tbody.innerHTML = rows
    .map((r, i) => `
      <tr>
        <td><strong>${i + 1}º</strong></td>
        <td><strong>${r.player}</strong></td>
        <td><strong class="text-emerald">${r.score} pts</strong></td>
        <td>${r.hits}</td>
        <td>${r.misses}</td>
        <td>${r.accuracy.toFixed(0)}%</td>
        <td class="subtle">${r.date}</td>
      </tr>
    `)
    .join("");
}
