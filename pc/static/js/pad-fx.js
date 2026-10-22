/**
 * Efectos gamer en botones: ripple al pulsar + clase is-down.
 * @author Cristian Deysdayr Jimenez
 * @created 2026-10-15
 */

/**
 * Lanza un ripple desde el punto del pointer.
 * @param {HTMLElement} el
 * @param {PointerEvent} ev
 * @returns {void}
 */
function spawnRipple(el, ev) {
  const rect = el.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const dot = document.createElement("span");
  dot.className = "ripple";
  dot.style.width = `${size}px`;
  dot.style.height = `${size}px`;
  dot.style.left = `${ev.clientX - rect.left - size / 2}px`;
  dot.style.top = `${ev.clientY - rect.top - size / 2}px`;
  el.appendChild(dot);
  window.setTimeout(() => dot.remove(), 560);
}

/**
 * Enlaza ripple e is-down a todos los controles del pad.
 * @returns {void}
 */
function bindPadFx() {
  document.querySelectorAll(".tile, .dkey").forEach((el) => {
    el.addEventListener("pointerdown", (ev) => {
      el.classList.add("is-down");
      spawnRipple(el, ev);
    });
    const up = () => el.classList.remove("is-down");
    el.addEventListener("pointerup", up);
    el.addEventListener("pointerleave", up);
    el.addEventListener("pointercancel", up);
  });
}

bindPadFx();
