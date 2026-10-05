// Mock builders for the prototype pages. Sample passwords are fixed strings:
// this file draws pixels, it never generates anything.
const G = {
  key: "\u{F0306}", refresh: "\u{F0450}", copy: "\u{F018F}", save: "\u{F0193}",
  gear: "\u{F0493}", check: "\u{F012C}", alert: "\u{F0026}", down: "\u{F0140}",
  back: "\u{F004D}", eye: "\u{F0208}", eyeOff: "\u{F0209}", open: "\u{F03CC}",
  lock: "\u{F033E}", vault: "\u{F127C}",
};
const SAMPLE = "tR7#vQe2-mXp9!Lw_k4Zs=Hb8";
const SAMPLE16 = "Qm4!vT9kR2#pLx7a";
const SAMPLE64 = "8kQ#mW2v!Lr9Tx_Pz4=bN7c-Hs3Fy+Jd6@Gq1$Vt5%Xa0^Ke8&Mu2*Cw4?Rf7Yp";

function tint(s) {
  return [...s].map(c => {
    const k = /[A-Z]/.test(c) ? "u" : /[a-z]/.test(c) ? "l" : /[0-9]/.test(c) ? "d" : "s";
    const e = c.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    return `<span class="${k}">${e}</span>`;
  }).join("");
}

function bar(state) {
  const cls = { ready: "", copied: "accent", unset: "dim", failed: "bad", hover: "" }[state] ?? "";
  const bang = state === "failed" ? '<span class="bang">!</span>' : "";
  const others = ["\u{F00AF}", "\u{F05A9}", "\u{F057E}", "\u{F0425}"]; // bluetooth, wifi, volume, power
  return `<div><div class="bar">
    <div class="slot mint ${cls} ${state === "hover" ? "hover" : ""}">${G.key}${bang}</div>
    ${others.map(o => `<div class="slot other">${o}</div>`).join("")}
  </div><div class="barlabel">${state}</div></div>`;
}

function hero({ icon = G.key, tone = "", title, meta, detail, trailing = G.gear }) {
  return `<div class="hero"><div class="icon ${tone}">${icon}</div>
    <div class="txt"><div class="title">${title}</div><div class="meta">${meta}</div>${detail ? `<div class="detail">${detail}</div>` : ""}</div>
    ${trailing ? `<div class="iconbtn">${trailing}</div>` : ""}</div>`;
}

function pwBox({ value = SAMPLE, bits = 156, rule = "24 chars · 4 classes", masked = false, pct = 100 }) {
  const long = value.length > 40 ? "long" : "";
  const shown = masked ? "•".repeat(Math.min(value.length, 24)) : tint(value);
  return `<div class="pw"><div class="val ${long} ${masked ? "masked" : ""}">${shown}</div>
    <div class="meter"><i style="width:${pct}%"></i></div>
    <div class="foot"><span>${bits} bits</span><span>${rule}</span></div></div>`;
}

function lengthRow(n = 24, max = 64) {
  const pct = Math.min(100, ((n - 4) / (max - 4)) * 100);
  return `<div class="row"><span class="lbl">Length</span>
    <div class="slider"><div class="track"><i style="width:${pct}%"></i></div><div class="knob" style="left:calc(${pct}% - 5px)"></div></div>
    <div class="num"><span>${n}</span><span>${G.down}</span></div></div>`;
}

function chips(on = ["A–Z", "a–z", "0–9", "!#$"], cur = -1) {
  return `<div class="chips">${["A–Z", "a–z", "0–9", "!#$"].map((c, i) =>
    `<div class="chip ${on.includes(c) ? "on" : ""} ${i === cur ? "cur" : ""}">${c}</div>`).join("")}</div>`;
}

function presetRow(v = "Default") {
  return `<div class="row"><span class="lbl">Preset</span><div class="dd"><span class="v">${v}</span><span class="car">${G.down}</span></div></div>`;
}

function btn(g, label, extra = "") { return `<span class="btn ${extra}"><span class="g">${g}</span>${label}</span>`; }

function actions(kind = "ready") {
  if (kind === "copied") return `<div class="actions">${btn(G.refresh, "New")}${btn(G.check, "Copied", "primary")}${btn(G.vault, "Save")}</div>`;
  return `<div class="actions">${btn(G.refresh, "New")}${btn(G.copy, "Copy", "primary cur")}${btn(G.vault, "Save")}</div>`;
}

function footer(text = "enter copy · ctrl+r new · ctrl+s save · esc close") { return `<div class="kbd">${text}</div>`; }

function field(label, value, { ph = "", focus = false } = {}) {
  const v = value ? `${value}${focus ? '<span class="caret"></span>' : ""}` : `<span class="ph">${ph}</span>${focus ? '<span class="caret"></span>' : ""}`;
  return `<div class="row"><span class="lbl">${label}</span><div class="field ${focus ? "focus" : ""}">${v}</div></div>`;
}

function setTheme(t) { document.documentElement.dataset.theme = t; try { localStorage.setItem("mint-proto-theme", t); } catch (e) {} }
function initTheme() {
  let t = new URLSearchParams(location.search).get("theme");
  if (!t) { try { t = localStorage.getItem("mint-proto-theme"); } catch (e) {} }
  setTheme(t || "light");
}

// Review round 1 builders.
function hero2({ icon = G.key, tone = "", title, meta, pill = "", trailing = G.gear }) {
  return `<div class="hero"><div class="icon ${tone}">${icon}</div>
    <div class="txt"><div class="title">${title}${pill ? `<span class="pill">${pill}</span>` : ""}</div><div class="meta">${meta}</div></div>
    ${trailing ? `<div class="iconbtn">${trailing}</div>` : ""}</div>`;
}
function pw2({ value = SAMPLE, bits = 141, len = 24, shown = false, note = "" }) {
  const long = value.length > 40 ? "long" : "";
  const v = shown ? value.replace(/&/g, "&amp;").replace(/</g, "&lt;") : "•".repeat(16);
  return `<div class="pw"><div class="top"><div class="val plain ${long} ${shown ? "" : "masked"}">${v}</div><div class="iconbtn">${shown ? G.eyeOff : G.eye}</div></div>
    <div class="foot"><span>${bits} bits</span><span>${note || len + " characters"}</span></div></div>`;
}
function rules2({ n = 24, on = ["A–Z", "a–z", "0–9", "!#$"], cur = -1, preset = "None", rule = "" } = {}) {
  const pct = Math.min(100, ((n - 4) / (64 - 4)) * 100);
  return `<div class="sep"></div><div class="sh">Password rules</div>
  <div class="ctl"><div class="cap"><span>Length</span><b>${rule || n + " characters"}</b></div>
   <div class="lenrow"><div class="slider"><div class="track"><i style="width:${pct}%"></i></div><div class="knob" style="left:calc(${pct}% - 5px)"></div></div>
   <div class="num"><span>${n}</span><span>${G.down}</span></div></div></div>
  <div class="ctl"><div class="cap"><span>Characters</span></div><div class="classes">${["A–Z", "a–z", "0–9", "!#$"].map((c, i) =>
    `<div class="b ${on.includes(c) ? "on" : ""} ${i === cur ? "cur" : ""}">${c}</div>`).join("")}</div></div>
  <div class="ctl"><div class="cap"><span>Site rule</span></div><div class="dd"><span class="v">${preset}</span><span class="car">${G.down}</span></div></div>`;
}
function ctlField(label, value, { ph = "", focus = false } = {}) {
  const v = value ? `${value}${focus ? '<span class="caret"></span>' : ""}` : `<span class="ph">${ph}</span>${focus ? '<span class="caret"></span>' : ""}`;
  return `<div class="ctl"><div class="cap"><span>${label}</span></div><div class="field ${focus ? "focus" : ""}">${v}</div></div>`;
}
function ctlDrop(label, value) { return `<div class="ctl"><div class="cap"><span>${label}</span></div><div class="dd"><span class="v">${value}</span><span class="car">${G.down}</span></div></div>`; }
function acts(list) { return `<div class="actions">${list.map(([g, l, x]) => btn(g, l, x || "")).join("")}</div>`; }
