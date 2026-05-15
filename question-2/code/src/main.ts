import "./style.css";
import { ParticleSystem } from "./particles/ParticleSystem";

/* ============================================================
   PARTICLE SYSTEM
   ============================================================ */
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

/* ============================================================
   NAVIGATION — MEGA MENUS
   ============================================================ */
const navItems = document.querySelectorAll<HTMLElement>(".nav-item[data-dropdown]");
let closeTimer: ReturnType<typeof setTimeout> | null = null;
let activeNavItem: HTMLElement | null = null;

function openMenu(item: HTMLElement) {
  if (closeTimer) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
  if (activeNavItem && activeNavItem !== item) {
    activeNavItem.classList.remove("open");
  }
  item.classList.add("open");
  activeNavItem = item;
}

function closeMenu(item: HTMLElement, delay = 200) {
  if (closeTimer) {
    clearTimeout(closeTimer);
  }
  closeTimer = setTimeout(() => {
    item.classList.remove("open");
    if (activeNavItem === item) {
      activeNavItem = null;
    }
  }, delay);
}

navItems.forEach((item) => {
  const trigger = item.querySelector<HTMLElement>(".nav-trigger");
  const menu = item.querySelector<HTMLElement>(".mega-menu");

  if (!trigger || !menu) return;

  trigger.addEventListener("click", (e) => {
    e.preventDefault();
    if (item.classList.contains("open")) {
      closeMenu(item, 0);
    } else {
      openMenu(item);
    }
  });

  item.addEventListener("mouseenter", () => {
    openMenu(item);
  });

  item.addEventListener("mouseleave", () => {
    closeMenu(item, 250);
  });
});

// Close on click outside
document.addEventListener("click", (e) => {
  if (activeNavItem && !activeNavItem.contains(e.target as Node)) {
    closeMenu(activeNavItem, 0);
  }
});

// Close on ESC
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    if (activeNavItem) {
      closeMenu(activeNavItem, 0);
    }
    // Also close video modal if open
    const modal = document.getElementById("video-modal");
    if (modal && !modal.hidden) {
      closeVideoModal();
    }
    // Close mobile drawer
    const drawer = document.getElementById("mobile-drawer");
    if (drawer && drawer.classList.contains("open")) {
      closeDrawer();
    }
  }
});

/* ============================================================
   HEADER SCROLL STATE
   ============================================================ */
const header = document.getElementById("site-header");
if (header) {
  window.addEventListener("scroll", () => {
    if (window.scrollY > 10) {
      header.classList.add("scrolled");
    } else {
      header.classList.remove("scrolled");
    }
  }, { passive: true });
}

/* ============================================================
   SMOOTH SCROLL for anchor links
   ============================================================ */
document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]').forEach((link) => {
  link.addEventListener("click", (e) => {
    const href = link.getAttribute("href");
    if (!href || href === "#") return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      // Close any open menu
      if (activeNavItem) {
        closeMenu(activeNavItem, 0);
      }
      // Close mobile drawer
      const drawer = document.getElementById("mobile-drawer");
      if (drawer && drawer.classList.contains("open")) {
        closeDrawer();
      }
    }
  });
});

/* ============================================================
   USE CASES TABS
   ============================================================ */
function initUseCaseTabs() {
  const tabs = document.querySelectorAll<HTMLButtonElement>(".uc-tab");
  const panels = document.querySelectorAll<HTMLElement>("[data-uc-panel]");

  function activateTab(tabName: string) {
    tabs.forEach((tab) => {
      const isActive = tab.dataset.uc === tabName;
      tab.classList.toggle("active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
    });
    panels.forEach((panel) => {
      const isActive = panel.dataset.ucPanel === tabName;
      panel.classList.toggle("active", isActive);
      panel.hidden = !isActive;
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      activateTab(tab.dataset.uc!);
    });
  });

  // Handle data-uc-tab links in nav and mega menus
  document.querySelectorAll<HTMLAnchorElement>("[data-uc-tab]").forEach((link) => {
    link.addEventListener("click", () => {
      const tabName = link.dataset.ucTab;
      if (tabName) {
        activateTab(tabName);
      }
    });
  });
}

initUseCaseTabs();

/* ============================================================
   MOBILE DRAWER
   ============================================================ */
const hamburger = document.getElementById("hamburger");
const drawer = document.getElementById("mobile-drawer");
const drawerBackdrop = document.getElementById("drawer-backdrop");

function openDrawer() {
  if (!drawer || !hamburger) return;
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  hamburger.classList.add("active");
  hamburger.setAttribute("aria-expanded", "true");
  document.body.style.overflow = "hidden";
}

function closeDrawer() {
  if (!drawer || !hamburger) return;
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
  hamburger.classList.remove("active");
  hamburger.setAttribute("aria-expanded", "false");
  document.body.style.overflow = "";
}

if (hamburger && drawer) {
  hamburger.addEventListener("click", () => {
    if (drawer.classList.contains("open")) {
      closeDrawer();
    } else {
      openDrawer();
    }
  });
}

if (drawerBackdrop) {
  drawerBackdrop.addEventListener("click", closeDrawer);
}

// Drawer accordion toggles
document.querySelectorAll<HTMLButtonElement>("[data-drawer-toggle]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetId = btn.dataset.drawerToggle;
    if (!targetId) return;
    const sub = document.getElementById(targetId);
    if (!sub) return;
    const isOpen = !sub.hidden;
    sub.hidden = !isOpen;
    btn.classList.toggle("open", !isOpen);
  });
});

// Handle uc-tab links in drawer
document.querySelectorAll<HTMLAnchorElement>("#mobile-drawer [data-uc-tab]").forEach((link) => {
  link.addEventListener("click", () => {
    const tabName = link.dataset.ucTab;
    if (tabName) {
      // Activate the tab
      const tabs = document.querySelectorAll<HTMLButtonElement>(".uc-tab");
      const panels = document.querySelectorAll<HTMLElement>("[data-uc-panel]");
      tabs.forEach((tab) => {
        const isActive = tab.dataset.uc === tabName;
        tab.classList.toggle("active", isActive);
        tab.setAttribute("aria-selected", String(isActive));
      });
      panels.forEach((panel) => {
        const isActive = panel.dataset.ucPanel === tabName;
        panel.classList.toggle("active", isActive);
        panel.hidden = !isActive;
      });
    }
    closeDrawer();
  });
});

/* ============================================================
   VIDEO PLAYBACK
   ============================================================ */
function setupVideoPlayer(videoId: string, btnId: string) {
  const video = document.getElementById(videoId) as HTMLVideoElement | null;
  const btn = document.getElementById(btnId) as HTMLButtonElement | null;

  if (!video || !btn) return;

  const togglePlay = () => {
    if (video!.paused) {
      video!.play();
      btn!.classList.add("hidden");
    } else {
      video!.pause();
      btn!.classList.remove("hidden");
    }
  };

  btn.addEventListener("click", togglePlay);

  video.addEventListener("click", togglePlay);

  video.addEventListener("play", () => {
    btn!.classList.add("hidden");
  });

  video.addEventListener("pause", () => {
    btn!.classList.remove("hidden");
  });

  // Keyboard support
  btn.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      togglePlay();
    }
  });
}

setupVideoPlayer("hero-video", "hero-play-btn");
setupVideoPlayer("product-video", "product-play-btn");

/* ============================================================
   VIDEO MODAL (for tile play buttons)
   ============================================================ */
const videoModal = document.getElementById("video-modal");
const videoModalPlayer = document.getElementById("video-modal-player") as HTMLVideoElement | null;
const videoModalClose = document.getElementById("video-modal-close");
const videoModalBackdrop = document.getElementById("video-modal-backdrop");

const videoMap: Record<string, string> = {
  "an-agent-first-experience": "/videos/an-agent-first-experience.mp4",
  "cross-surface-agents": "/videos/cross-surface-agents.mp4",
  "higher-level-abstractions": "/videos/higher-level-abstractions.mp4",
  "user-feedback": "/videos/user-feedback.mp4",
};

function openVideoModal(src: string) {
  if (!videoModal || !videoModalPlayer) return;
  videoModalPlayer.src = src;
  videoModal.hidden = false;
  document.body.style.overflow = "hidden";
  videoModalPlayer.play();
}

function closeVideoModal() {
  if (!videoModal || !videoModalPlayer) return;
  videoModalPlayer.pause();
  videoModalPlayer.src = "";
  videoModal.hidden = true;
  document.body.style.overflow = "";
}

if (videoModalClose) {
  videoModalClose.addEventListener("click", closeVideoModal);
}

if (videoModalBackdrop) {
  videoModalBackdrop.addEventListener("click", closeVideoModal);
}

// Tile play buttons
document.querySelectorAll<HTMLButtonElement>("[data-video]").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    const key = btn.dataset.video;
    if (key && videoMap[key]) {
      openVideoModal(videoMap[key]);
    }
  });
});

/* ============================================================
   INTERSECTION OBSERVER — Fade in sections
   ============================================================ */
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -60px 0px",
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll("section").forEach((section) => {
  observer.observe(section);
});