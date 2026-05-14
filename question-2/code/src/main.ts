import "./style.css";
import { ParticleSystem } from "./particles/ParticleSystem";

const canvas = document.querySelector<HTMLCanvasElement>("#motion-field");
const debugPanel = document.querySelector<HTMLElement>("#debug-panel");

if (!canvas) {
  throw new Error("Missing #motion-field canvas.");
}

const debugEnabled = new URLSearchParams(window.location.search).get("debug") === "1";
const captureMode = new URLSearchParams(window.location.search).get("capture");
if (debugPanel && debugEnabled) {
  debugPanel.hidden = false;
}

const system = new ParticleSystem(canvas, debugPanel);
system.start();

if (captureMode === "hover" || captureMode === "click") {
  document.body.classList.add(`capture-${captureMode}`);
  const x = Math.round(window.innerWidth * 0.5);
  const y = Math.round(window.innerHeight * 0.64);
  window.setTimeout(() => {
    window.dispatchEvent(new PointerEvent("pointermove", { clientX: x, clientY: y, bubbles: true }));
    if (captureMode === "click") {
      window.dispatchEvent(new PointerEvent("pointerdown", { clientX: x, clientY: y, bubbles: true }));
    }
  }, 360);
}

window.addEventListener("beforeunload", () => {
  system.stop();
});

window.__ANTIGRAVITY_RECREATION__ = {
  getStats: () => system.getStats(),
};

declare global {
  interface Window {
    __ANTIGRAVITY_RECREATION__: {
      getStats: () => { fps: number; particles: number; reducedMotion: boolean };
    };
  }
}
