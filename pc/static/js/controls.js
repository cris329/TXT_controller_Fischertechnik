/**
 * Dashboard: teleop + video por snaps rapidos (mejor en hotspot).
 * @author Cristian Deysdayr Jimenez
 * @created 2026-10-13
 */

/** @param {string} path @param {object} [body] @returns {Promise<void>} */
async function post(path, body) {
  await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : "{}",
  });
}

/** @param {number} vx @param {number} vy @param {number} omega @returns {Promise<void>} */
function drive(vx, vy, omega) {
  updateDir(vx, vy, omega);
  return post("/api/drive", { vx, vy, omega });
}

/** @param {string} id @param {string} text @param {boolean} [ok] @returns {void} */
function setText(id, text, ok) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  if (ok !== undefined) el.classList.toggle("bad", !ok);
}

/** @param {string} id @param {boolean} on @returns {void} */
function setDot(id, on) {
  document.getElementById(id)?.classList.toggle("on", !!on);
}

/** @param {number} vx @param {number} vy @param {number} omega @returns {void} */
function updateDir(vx, vy, omega) {
  const moving = Math.abs(vx) > 0.05 || Math.abs(vy) > 0.05;
  let label = "Detenido";
  if (moving && omega < 0) label = "Curva izq.";
  else if (moving && omega > 0) label = "Curva der.";
  else if (omega < 0) label = "Gira izq.";
  else if (omega > 0) label = "Gira der.";
  else if (vx > 0) label = "Avance";
  else if (vx < 0) label = "Retroceso";
  else if (vy < 0) label = "Izquierda";
  else if (vy > 0) label = "Derecha";
  setText("dir-state", label === "Detenido" ? "Recto" : label);
  setText(
    "run-state",
    label === "Detenido" || label === "Recto" ? "Detenido" : "En movimiento",
  );
}

function bindButtons() {
  document.querySelectorAll("button[data-vx]").forEach((btn) => {
    const send = () => drive(+btn.dataset.vx, +btn.dataset.vy, +btn.dataset.omega);
    const stop = () => drive(0, 0, 0);
    btn.addEventListener("pointerdown", send);
    btn.addEventListener("pointerup", stop);
    btn.addEventListener("pointerleave", stop);
  });
  document.getElementById("kick").onclick = () => post("/api/kick");
  document.getElementById("sound").onclick = () => post("/api/sound");
  const stopBtn = document.getElementById("stop");
  if (stopBtn) {
    stopBtn.onclick = () => {
      drive(0, 0, 0);
      post("/api/stop");
    };
  }
  const restart = document.getElementById("restart");
  if (restart) restart.onclick = () => post("/api/restart");
}

let lastUrl = null;
let camBusy = false;

/** Snap inmediato del buffer PC (sin acumular peticiones). @returns {Promise<boolean>} */
async function refreshCamera() {
  if (camBusy) return false;
  camBusy = true;
  const img = document.getElementById("feed");
  try {
    const res = await fetch("/camera.jpg?t=" + Date.now(), { cache: "no-store" });
    if (!res.ok || res.status === 204) return false;
    const blob = await res.blob();
    if (!blob || blob.size < 80) return false;
    const url = URL.createObjectURL(blob);
    const prev = lastUrl;
    lastUrl = url;
    img.src = url;
    if (prev) URL.revokeObjectURL(prev);
    return true;
  } catch (e) {
    return false;
  } finally {
    camBusy = false;
  }
}

/** @param {string|object} raw @returns {{ok: boolean, label: string}} */
function mqttLabel(raw) {
  const text = typeof raw === "string" ? raw : JSON.stringify(raw || "");
  const ok = /"ok"\s*:\s*true/.test(text) || text === "connected";
  return { ok, label: ok ? "OK" : (text.slice(0, 32) || "—") };
}

/** @returns {Promise<void>} */
async function refreshMeta() {
  try {
    const s = await fetch("/api/status").then((r) => r.json());
    const liveOk = !!s.video;
    setText("live", liveOk ? "EN VIVO" : "sin video", liveOk);
    document.getElementById("pill-live")?.classList.toggle("on", liveOk);
    setText("xbox", s.xbox ? "SI" : "no", !!s.xbox);
    setText("host", s.host || "—");
    setText("cam-hb", "HB " + (s.heartbeat || "—"));
  } catch (e) {
    setText("live", "error", false);
  }
}

bindButtons();
setInterval(() => {
  refreshCamera();
}, 55);
setInterval(refreshMeta, 600);
refreshCamera();
refreshMeta();
