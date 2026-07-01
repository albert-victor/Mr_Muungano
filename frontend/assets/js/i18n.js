/** Bilingual UI strings — Kiswahili & English */
export const STRINGS = {
  sw: {
    metaDescription: "Mr. Muungano — Msaidizi wa AI wa Elimu ya Muungano wa Tanganyika na Zanzibar",
    pageTitle: "Mr. Muungano — Elimu ya Muungano",
    brandSub: "Elimu ya Muungano wa Tanzania",
    toneLabel: "Mtindo wa Majibu",
    toneDefault: "Otomatiki",
    toneOfficial: "Rasmi",
    toneStudent: "Mwanafunzi",
    toneYouth: "Kijana / Rahisi",
    toneSimple: "Eleza kama mtoto wa miaka 10",
    suggestionsLabel: "Maswali ya Mwongozo",
    statusLabel: "Hali ya Maktaba",
    statusChecking: "Inaangalia…",
    statusWarming: "Inapakia modeli ya AI…",
    statusReady: "vipande vya nyaraka",
    statusEmpty: "Maktaba haijajazwa — endesha ingest.py",
    statusNoKey: "Hakuna API key",
    statusServerDown: "Server haifanyi kazi",
    footerSources: "Vyanzo: Tovuti rasmi, Katiba, Sheria & Machapisho ya Serikali",
    landingTitle: "Uliza kuhusu Muungano",
    landingSub: "Majibu kutoka vyanzo rasmi",
    settingsToggle: "Mipangilio",
    inputPlaceholder: "Andika swali lako hapa…",
    referencesTitle: "Marejeo",
    referencesSub: "Vyanzo vilivyotumika kujibu swali lako.",
    referencesEmpty: "Bofya \"Angalia marejeo\" kwenye jibu ili kuona vyanzo vilivyotumika.",
    referencesNone: "Hakuna marejeo yaliyopatikana kwa swali hili.",
    citationsPage: "Ukurasa",
    viewCitations: "Angalia marejeo",
    closeReferences: "Funga marejeo",
    themeToggle: "Badilisha mandhari",
    statusSearching: "Inatafuta vyanzo…",
    statusPreparing: "Inaandaa jibu lako…",
    statusGenerating: "Inaandika…",
    suggestionsFail: "Imeshindwa kupakia maswali.",
    errorPrefix: "Samahani, kumetokea hitilafu:",
    openMenu: "Fungua menyu",
    clearChat: "Futa mazungumzo",
    clearChatTitle: "Anza upya",
    langSwitch: "Lugha",
    typingLabel: "Mr. Muungano anaandika",
    copyDone: "Imenakiliwa!",
    copyLabel: "Nakili",
  },
  en: {
    metaDescription: "Mr. Muungano — AI assistant for education on the Union of Tanganyika and Zanzibar",
    pageTitle: "Mr. Muungano — Union Education",
    brandSub: "Union Education for Tanzania",
    toneLabel: "Response Style",
    toneDefault: "Automatic",
    toneOfficial: "Official",
    toneStudent: "Student",
    toneYouth: "Youth / Casual",
    toneSimple: "Explain like I'm 10",
    suggestionsLabel: "Suggested Questions",
    statusLabel: "Knowledge Base",
    statusChecking: "Checking…",
    statusWarming: "Loading AI model…",
    statusReady: "document chunks loaded",
    statusEmpty: "Knowledge base empty — run ingest.py",
    statusNoKey: "No API key",
    statusServerDown: "Server is not running",
    footerSources: "Sources: Constitution, Articles of Union, Acts & Official publications",
    landingTitle: "Ask about the Union",
    landingSub: "Answers from official sources",
    settingsToggle: "Settings",
    inputPlaceholder: "Type your question here…",
    referencesTitle: "References",
    referencesSub: "Sources used to answer your question.",
    referencesEmpty: "Click \"View references\" on an answer to see the sources used.",
    referencesNone: "No references found for this question.",
    citationsPage: "Page",
    viewCitations: "View references",
    closeReferences: "Close references",
    themeToggle: "Toggle theme",
    statusSearching: "Searching sources…",
    statusPreparing: "Getting your answer ready…",
    statusGenerating: "Writing…",
    suggestionsFail: "Failed to load suggestions.",
    errorPrefix: "Sorry, an error occurred:",
    openMenu: "Open menu",
    clearChat: "Clear conversation",
    clearChatTitle: "Start fresh",
    langSwitch: "Language",
    typingLabel: "Mr. Muungano is typing",
    copyDone: "Copied!",
    copyLabel: "Copy",
  },
};

export const SUGGESTIONS = {
  sw: [
    "Muungano ulianzishwa lini?",
    "Kwa nini serikali mbili?",
    "Mambo ya Muungano ni yapi?",
    "Nani alisaini Hati ya Muungano?",
    "Tofauti ya Bara na Zanzibar?",
    "Eleza Muungano kwa urahisi.",
  ],
  en: [
    "When was the Union established?",
    "Why two governments?",
    "What are Union Matters?",
    "Who signed the Articles of Union?",
    "Mainland vs Zanzibar?",
    "Explain the Union simply.",
  ],
};

export function getLang() {
  return localStorage.getItem("muungano_lang") === "en" ? "en" : "sw";
}

export function setLang(lang) {
  localStorage.setItem("muungano_lang", lang);
  document.documentElement.lang = lang;
}

export function t(key) {
  const lang = getLang();
  return STRINGS[lang][key] ?? STRINGS.sw[key] ?? key;
}
