/**
 * Teclado: flechas avance+giro combinables (WASD/QE igual).
 * @author Cristian Deysdayr Jimenez
 * @created 2026-10-16
 */

/** Escala de giro al ir en movimiento (evita anular avance). */
const TURN_MOVING = 0.4;

/**
 * Suma ejes de teclas pulsadas y atenua giro si hay traslacion.
 * @param {Iterable<string>} codes
 * @param {Record<string, number[]>} axes
 * @returns {[number, number, number]}
 */
function mergeKeyAxes(codes, axes) {
  let vx = 0;
  let vy = 0;
  let omega = 0;
  for (const code of codes) {
    const a = axes[code];
    if (!a) continue;
    vx += a[0];
    vy += a[1];
    omega += a[2];
  }
  vx = Math.max(-1, Math.min(1, vx));
  vy = Math.max(-1, Math.min(1, vy));
  omega = Math.max(-1, Math.min(1, omega));
  if ((Math.abs(vx) > 0.05 || Math.abs(vy) > 0.05) && omega) {
    omega *= TURN_MOVING;
  }
  return [vx, vy, omega];
}

/** @returns {string|null} codigo de eje o null */
function axisCode(e) {
  if (e.code && e.code !== "Unidentified") return e.code;
  const k = e.key;
  if (k === "ArrowUp" || k === "Up") return "ArrowUp";
  if (k === "ArrowDown" || k === "Down") return "ArrowDown";
  if (k === "ArrowLeft" || k === "Left") return "ArrowLeft";
  if (k === "ArrowRight" || k === "Right") return "ArrowRight";
  return null;
}

/** Escucha teclas (capture) y publica drive combinado. @returns {void} */
function bindKeyboard() {
  const pressed = new Set();
  const axes = {
    ArrowUp: [1, 0, 0],
    ArrowDown: [-1, 0, 0],
    ArrowLeft: [0, 0, -1],
    ArrowRight: [0, 0, 1],
    KeyW: [1, 0, 0],
    KeyS: [-1, 0, 0],
    KeyA: [0, 0, -1],
    KeyD: [0, 0, 1],
    KeyQ: [0, 0, -1],
    KeyE: [0, 0, 1],
  };
  let holdTimer = null;

  /** @returns {void} */
  function sync() {
    const vals = mergeKeyAxes(pressed, axes);
    drive(...vals);
  }

  /** @returns {void} */
  function startHold() {
    if (holdTimer) return;
    holdTimer = globalThis.setInterval(sync, 180);
  }

  /** @returns {void} */
  function stopHold() {
    if (!holdTimer) return;
    globalThis.clearInterval(holdTimer);
    holdTimer = null;
  }

  document.addEventListener(
    "keydown",
    (e) => {
      if (e.code === "Space" || e.key === " ") {
        e.preventDefault();
        if (!e.repeat) post("/api/kick");
        return;
      }
      if (e.code === "KeyX" || e.key === "x" || e.key === "X") {
        if (!e.repeat) {
          drive(0, 0, 0);
          post("/api/stop");
        }
        return;
      }
      const code = axisCode(e);
      if (!code || !axes[code]) return;
      e.preventDefault();
      e.stopPropagation();
      if (pressed.has(code)) return;
      pressed.add(code);
      sync();
      startHold();
    },
    true,
  );

  document.addEventListener(
    "keyup",
    (e) => {
      const code = axisCode(e);
      if (!code || !axes[code]) return;
      e.preventDefault();
      pressed.delete(code);
      if (pressed.size === 0) stopHold();
      sync();
    },
    true,
  );

  window.addEventListener("blur", () => {
    pressed.clear();
    stopHold();
    drive(0, 0, 0);
  });
}

bindKeyboard();
