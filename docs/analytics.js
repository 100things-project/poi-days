(() => {
  "use strict";
  const GA_ID = "G-0TZ7EH65BW";
  const OWNER_KEY = "poidays_owner_exclude_v1";

  const params = new URLSearchParams(location.search);
  if (params.get("owner") === "1") localStorage.setItem(OWNER_KEY, "1");
  if (params.get("owner") === "0") localStorage.removeItem(OWNER_KEY);
  if (localStorage.getItem(OWNER_KEY) === "1") window["ga-disable-" + GA_ID] = true;
  if (params.has("owner")) {
    params.delete("owner");
    const q = params.toString();
    history.replaceState(null, "", location.pathname + (q ? "?" + q : "") + location.hash);
  }

  window.dataLayer = window.dataLayer || [];
  if (typeof window.gtag !== "function") {
    window.gtag = function(){ window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", GA_ID);
    if (!document.querySelector('script[src*="' + GA_ID + '"]')) {
      const s = document.createElement("script");
      s.async = true;
      s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
      document.head.appendChild(s);
    }
  }

  if (document.documentElement.hasAttribute("data-poidays-analytics-installed")) return;
  document.documentElement.setAttribute("data-poidays-analytics-installed", "");

  const send = (name, extra = {}) => {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", name, {
      page_path: location.pathname + location.search,
      ...extra
    });
  };
  const textOf = (el) => (el?.textContent || "").replace(/\s+/g, " ").trim().slice(0, 120);

  document.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target) return;

    if (target.closest("[data-copy]")) {
      send("invite_copy", { copy_type: target.closest("[data-copy]").getAttribute("data-copy") || "unknown" });
    }

    const a = target.closest("a[href]");
    if (!a) return;
    let url = null;
    try { url = new URL(a.href, location.href); } catch {}
    const href = a.getAttribute("href") || "";
    const base = {
      link_text: textOf(a),
      link_url: url?.href || href
    };

    if (/invite\.php\?invite=/i.test(href)) {
      send("invite_click", base);
    } else if (/pc\.moppy\.jp\/ad\/detail\.php/i.test(url?.href || "")) {
      send("moppy_offer_click", base);
    } else if (href.startsWith("#diagnosis") || /#diagnosis$/.test(url?.href || "")) {
      send("diagnosis_start", { trigger_text: textOf(a) });
    } else if (url && url.origin !== location.origin) {
      send("outbound_click", { ...base, destination_host: url.hostname });
    } else {
      send("internal_link_click", base);
    }
  }, true);

  document.addEventListener("change", (event) => {
    const el = event.target;
    if (!(el instanceof HTMLInputElement) || el.type !== "radio") return;
    const quiz = el.closest("#quiz");
    if (!quiz) return;
    const names = [...new Set([...quiz.querySelectorAll('input[type="radio"]')].map(x => x.name))];
    const answered = names.filter(name => quiz.querySelector('input[name="' + CSS.escape(name) + '"]:checked')).length;
    send("diagnosis_progress", { question_name: el.name, answered_count: answered });
  }, true);

  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (form.id === "quiz") send("diagnosis_complete");
    if (form.id === "point-plan") send("planner_complete");
  }, true);

  document.addEventListener("toggle", (event) => {
    const d = event.target;
    if (!(d instanceof HTMLDetailsElement) || !d.open) return;
    const summary = d.querySelector("summary");
    send("faq_open", { summary_text: textOf(summary) });
  }, true);
})();