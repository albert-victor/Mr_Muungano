/**
 * MuunganoAi — Frontend Chat Client (Dira-style UI)
 */
import { getLang, setLang, t } from "./i18n.js";
import { formatMarkdown, formatStreaming, escapeHtml, escapeAttr } from "./markdown.js";

const API = "";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);
const chatMessages = $("#chat-messages");
const chatForm = $("#chat-form");
const messageInput = $("#message-input");
const sendBtn = $("#send-btn");
const welcomeSuggestionsEl = $("#welcome-suggestions");
const statusDot = $("#status-dot");
const statusText = $("#status-text");
const toneSelect = $("#tone-select");
const referencesList = $("#references-list");
const referencesDrawer = $("#references-drawer");
const welcomeEl = $("#welcome");
const overlay = $("#overlay");
const settingsPanel = $("#settings-panel");

const SUGGESTION_ICONS = [
  "fa-calendar-days",
  "fa-landmark",
  "fa-list-check",
  "fa-pen-nib",
  "fa-map-location-dot",
  "fa-lightbulb",
];

let history = [];
let isLoading = false;
let serverReady = false;
let scrollPending = false;

// ─── Theme ──────────────────────────────────────────────────────────────────

function getTheme() {
  return localStorage.getItem("muungano_theme") === "light" ? "light" : "dark";
}

function setTheme(theme) {
  localStorage.setItem("muungano_theme", theme);
  document.documentElement.setAttribute("data-theme", theme);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = theme === "light" ? "#1eb53a" : "#0a1410";
}

function toggleTheme() {
  setTheme(getTheme() === "dark" ? "light" : "dark");
}

// ─── i18n ───────────────────────────────────────────────────────────────────

function applyLanguage(lang) {
  setLang(lang);
  document.documentElement.lang = lang;
  document.title = t("pageTitle");
  const meta = $("#meta-description");
  if (meta) meta.content = t("metaDescription");

  $$("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (key) el.textContent = t(key);
  });

  $$("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });

  $$("[data-i18n-aria]").forEach((el) => {
    el.setAttribute("aria-label", t(el.dataset.i18nAria));
  });

  $$("[data-i18n-title]").forEach((el) => {
    el.setAttribute("title", t(el.dataset.i18nTitle));
  });

  $$(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === lang);
  });

  if (!isLoading) {
    loadSuggestions();
    checkHealth();
  }
}

// ─── Init ───────────────────────────────────────────────────────────────────

async function init() {
  setTheme(getTheme());
  applyLanguage(getLang());
  bindEvents();
  autoResizeTextarea();
  sendBtn.disabled = true;
  messageInput.disabled = true;
  await checkHealth();
  if (!serverReady) {
    const poll = setInterval(async () => {
      await checkHealth();
      if (serverReady) clearInterval(poll);
    }, 2000);
  }
  await loadSuggestions();
}

async function checkHealth() {
  try {
    const res = await fetch(`${API}/api/health`);
    const data = await res.json();

    serverReady = Boolean(data.retriever_ready);

    if (!serverReady) {
      statusDot.className = "status-dot warn";
      statusText.textContent = t("statusWarming");
      sendBtn.disabled = true;
      messageInput.disabled = true;
      return;
    }

    messageInput.disabled = false;
    if (!isLoading) sendBtn.disabled = false;

    if (data.knowledge_ready) {
      statusDot.className = "status-dot ready";
      statusText.textContent = `${data.chunk_count.toLocaleString()} ${t("statusReady")}`;
    } else {
      statusDot.className = "status-dot warn";
      statusText.textContent = t("statusEmpty");
    }

    if (!data.has_api_key) {
      statusText.textContent += ` · ${t("statusNoKey")}`;
    }
  } catch {
    serverReady = false;
    statusDot.className = "status-dot error";
    statusText.textContent = t("statusServerDown");
    sendBtn.disabled = true;
    messageInput.disabled = true;
  }
}

function renderSuggestionButtons(questions) {
  return questions
    .map(
      (q, idx) =>
        `<button type="button" class="suggestion-btn" data-q="${escapeAttr(q)}" style="animation-delay:${idx * 60}ms">
          <i class="fa-solid ${SUGGESTION_ICONS[idx] || "fa-circle-question"}"></i>
          <span>${escapeHtml(q)}</span>
        </button>`
    )
    .join("");
}

async function loadSuggestions() {
  const lang = getLang();
  try {
    const res = await fetch(`${API}/api/suggestions?lang=${lang}`);
    const data = await res.json();
    welcomeSuggestionsEl.innerHTML = renderSuggestionButtons(data.questions);
  } catch {
    welcomeSuggestionsEl.innerHTML = `<p class="references-empty">${t("suggestionsFail")}</p>`;
  }
}

function bindEvents() {
  chatForm.addEventListener("submit", onSubmit);

  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.requestSubmit();
    }
  });

  messageInput.addEventListener("input", autoResizeTextarea);

  welcomeSuggestionsEl.addEventListener("click", onSuggestionClick);

  $$(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => onLanguageChange(btn.dataset.lang));
  });

  $("#theme-toggle").addEventListener("click", toggleTheme);

  $("#brand-home").addEventListener("click", (e) => {
    e.preventDefault();
    clearChat();
  });

  $("#settings-toggle").addEventListener("click", (e) => {
    e.stopPropagation();
    const open = settingsPanel.hasAttribute("hidden");
    if (open) settingsPanel.removeAttribute("hidden");
    else settingsPanel.setAttribute("hidden", "");
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".settings-wrap")) {
      settingsPanel.setAttribute("hidden", "");
    }

    const citeBtn = e.target.closest(".btn-citations");
    if (citeBtn) openReferencesForMessage(citeBtn.closest(".message"));

    const copyBtn = e.target.closest(".btn-copy");
    if (copyBtn) copyMessage(copyBtn);
  });

  $("#clear-chat").addEventListener("click", clearChat);
  $("#references-close").addEventListener("click", closeReferencesDrawer);
  overlay.addEventListener("click", closeReferencesDrawer);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeReferencesDrawer();
      settingsPanel.setAttribute("hidden", "");
    }
  });
}

function onSuggestionClick(e) {
  const btn = e.target.closest(".suggestion-btn");
  if (!btn) return;
  messageInput.value = btn.dataset.q;
  autoResizeTextarea();
  chatForm.requestSubmit();
}

function openReferencesDrawer() {
  referencesDrawer.classList.add("open");
  referencesDrawer.setAttribute("aria-hidden", "false");
  overlay.classList.add("visible");
}

function closeReferencesDrawer() {
  referencesDrawer.classList.remove("open");
  referencesDrawer.setAttribute("aria-hidden", "true");
  overlay.classList.remove("visible");
}

function openReferencesForMessage(messageEl) {
  if (!messageEl) return;
  const citations = JSON.parse(messageEl.dataset.citations || "[]");
  renderReferences(citations);
  openReferencesDrawer();
}

// ─── Chat ───────────────────────────────────────────────────────────────────

async function onSubmit(e) {
  e.preventDefault();
  if (!serverReady) return;
  const text = messageInput.value.trim();
  if (!text || isLoading) return;

  hideWelcome();
  appendMessage("user", text);
  messageInput.value = "";
  autoResizeTextarea();
  history.push({ role: "user", content: text });

  isLoading = true;
  sendBtn.disabled = true;
  sendBtn.classList.add("is-sending");

  const typingEl = showTyping(t("statusPreparing"));

  try {
    await streamChat(text, typingEl);
  } catch (err) {
    typingEl.remove();
    appendMessage("bot", `${t("errorPrefix")} ${err.message}`);
  } finally {
    isLoading = false;
    sendBtn.disabled = false;
    sendBtn.classList.remove("is-sending");
    messageInput.focus();
  }
}

async function streamChat(message, typingEl) {
  const res = await fetch(`${API}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      history: history.slice(0, -1),
      tone: toneSelect.value,
      lang: getLang(),
      stream: true,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  let botBubble = null;
  let contentEl = null;
  let fullText = "";
  let hasStarted = false;
  let messageCitations = [];

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const event = JSON.parse(line);

        if (event.type === "status") {
          const label =
            event.data === "generating"
              ? t("statusGenerating")
              : event.data === "searching"
                ? t("statusSearching")
                : t("statusPreparing");
          updateTypingLabel(typingEl, label);
        } else if (event.type === "citations") {
          messageCitations = event.data;
        } else if (event.type === "token") {
          if (!hasStarted) {
            hasStarted = true;
            botBubble = convertTypingToResponse(typingEl);
            contentEl = botBubble.querySelector(".message__content");
          }
          fullText += event.data;
          contentEl.innerHTML = formatStreaming(fullText) + '<span class="stream-cursor" aria-hidden="true"></span>';
          scheduleScroll();
        } else if (event.type === "done") {
          if (event.data?.truncated) {
            fullText += getLang() === "en"
              ? "\n\n*(Response was cut short — ask me to continue.)*"
              : "\n\n*(Jibu lilikatika — niambie nieleze zaidi.)*";
          }
        }
      } catch {
        /* skip malformed */
      }
    }
  }

  if (!hasStarted) {
    typingEl.remove();
    botBubble = appendMessage("bot", fullText || "…");
    contentEl = botBubble.querySelector(".message__content");
  } else {
    contentEl.innerHTML = formatMarkdown(fullText);
    botBubble.classList.remove("is-streaming");
    botBubble.querySelector(".message__avatar")?.classList.remove("is-pulsing");
  }

  if (botBubble) {
    botBubble.dataset.citations = JSON.stringify(messageCitations);
    addMessageActions(botBubble, fullText, messageCitations);
  }

  history.push({ role: "assistant", content: fullText });
  scheduleScroll();
}

function updateTypingLabel(typingEl, label) {
  const el = typingEl?.querySelector(".typing-indicator__label");
  if (el) el.textContent = label;
}

function convertTypingToResponse(typingEl) {
  const bubble = typingEl.querySelector(".message__bubble");
  bubble.innerHTML = '<div class="message__content"></div>';
  typingEl.classList.add("is-streaming");
  typingEl.classList.remove("message--typing");
  typingEl.querySelector(".message__avatar")?.classList.add("is-pulsing");
  return typingEl;
}

// ─── UI Helpers ─────────────────────────────────────────────────────────────

function hideWelcome() {
  if (welcomeEl) welcomeEl.style.display = "none";
  chatMessages.classList.add("chat-messages--chatting");
}

function avatarIcon(role) {
  if (role === "user") return '<i class="fa-solid fa-user"></i>';
  return '<i class="fa-solid fa-comments"></i>';
}

function appendMessage(role, content) {
  const isUser = role === "user";
  const div = document.createElement("div");
  div.className = `message message--${isUser ? "user" : "bot"} message--enter`;
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  div.innerHTML = `
    <div class="message__avatar" aria-hidden="true">${avatarIcon(role)}</div>
    <div class="message__col">
      <div class="message__meta">
        <span class="message__name">${isUser ? (getLang() === "en" ? "You" : "Wewe") : "MuunganoAi"}</span>
        <span class="message__time">${time}</span>
      </div>
      <div class="message__bubble">
        <div class="message__content">${isUser ? `<p class="md-p">${escapeHtml(content)}</p>` : formatMarkdown(content)}</div>
      </div>
    </div>
  `;
  chatMessages.appendChild(div);
  if (!isUser && content) addMessageActions(div, content, []);
  scheduleScroll();
  return div;
}

function showTyping(label) {
  const div = document.createElement("div");
  div.className = "message message--bot message--typing message--enter";
  div.innerHTML = `
    <div class="message__avatar is-pulsing" aria-hidden="true">${avatarIcon("bot")}</div>
    <div class="message__col">
      <div class="message__meta">
        <span class="message__name">MuunganoAi</span>
      </div>
      <div class="message__bubble message__bubble--typing">
        <div class="typing-indicator">
          <span class="typing-indicator__label">${escapeHtml(label)}</span>
          <span class="typing-dots" aria-hidden="true">
            <span></span><span></span><span></span>
          </span>
        </div>
      </div>
    </div>
  `;
  chatMessages.appendChild(div);
  scheduleScroll();
  return div;
}

function addMessageActions(messageEl, text, citations) {
  if (messageEl.querySelector(".message__actions")) return;
  const bubble = messageEl.querySelector(".message__bubble");
  const actions = document.createElement("div");
  actions.className = "message__actions";
  actions.innerHTML = `
    ${citations.length ? `
    <button type="button" class="btn-citations">
      <i class="fa-solid fa-bookmark"></i>
      ${t("viewCitations")} (${citations.length})
    </button>` : ""}
    <button type="button" class="btn-copy" data-text="${escapeAttr(text)}">
      <i class="fa-regular fa-copy"></i>
      ${t("copyLabel")}
    </button>
  `;
  bubble.appendChild(actions);
}

async function copyMessage(btn) {
  const text = btn.dataset.text;
  try {
    await navigator.clipboard.writeText(text);
    const orig = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-check"></i> ${t("copyDone")}`;
    setTimeout(() => {
      btn.innerHTML = orig;
    }, 2000);
  } catch {
    /* clipboard blocked */
  }
}

function renderReferences(citations) {
  if (!citations.length) {
    referencesList.innerHTML = `<p class="references-empty">${t("referencesNone")}</p>`;
    return;
  }

  referencesList.innerHTML = citations
    .map(
      (c, idx) => `
    <article class="citation-card" style="animation-delay:${idx * 60}ms">
      <div class="citation-card__type">
        <i class="fa-solid fa-file-lines"></i>
        ${escapeHtml(c.document_type || "document")}
      </div>
      <h3 class="citation-card__title">${escapeHtml(c.document_title || c.document_name || "")}</h3>
      <p class="citation-card__meta">
        ${c.page ? `${t("citationsPage")} ${c.page} · ` : ""}${escapeHtml(c.source_url || c.source_file || "")}
      </p>
      <p class="citation-card__excerpt">${escapeHtml(c.excerpt)}</p>
    </article>
  `
    )
    .join("");
}

async function clearChat() {
  history = [];
  chatMessages.innerHTML = "";
  chatMessages.classList.remove("chat-messages--chatting");
  if (welcomeEl) {
    welcomeEl.style.display = "";
    chatMessages.appendChild(welcomeEl);
  }
  await loadSuggestions();
  closeReferencesDrawer();
  referencesList.innerHTML = `<p class="references-empty">${t("referencesEmpty")}</p>`;
  messageInput.focus();
}

function onLanguageChange(lang) {
  applyLanguage(lang);
  if (history.length > 0) {
    clearChat();
  }
}

function scheduleScroll() {
  if (scrollPending) return;
  scrollPending = true;
  requestAnimationFrame(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
    scrollPending = false;
  });
}

function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
}

init();
