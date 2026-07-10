# PROPOSAL YA MRADI

## MuunganoAi
### Msaidizi wa AI wa Elimu ya Muungano wa Tanganyika na Zanzibar

**Mada:** Akili Unde kwa Maendeleo — Elimu ya Uraia kwa Kizazi cha Kidijitali  
**Toleo:** 1.0 | Julai 2026  
**Hali ya Utekelezaji:** ~90% imekamilika (prototype inayofanya kazi)

---

## 1. Muhtasari wa Mkurugenzi

MuunganoAi ni mfumo wa akili bandia unaosaidia Watanzania — hasa vijana — kuelewa **Muungano wa Tanganyika na Zanzibar** kwa njia rahisi, ya kuaminika, na inayopatikana. Badala ya kusoma mamia ya kurasa za Katiba na Hati za Muungano, mtumiaji anauliza swali na kupata jibu linalotokana na **nyaraka rasmi tu** — si kutoka kwa mawazo ya AI peke yake.

Mfumo unatumia teknolojia ya **RAG (Retrieval-Augmented Generation)**: kwanza unatafuta taarifa sahihi kutoka maktaba ya nyaraka zilizothibitishwa, kisha AI inaandika jibu kulingana na vyanzo hivyo. Mtumiaji anaweza kuwasiliana kwa **maandishi au sauti**, kwa **Kiswahili au Kiingereza**, na kwa mtindo unaomfaa (vijana, mwanafunzi, rasmi).

**Lengo kuu:** kuongeza uelewa wa Muungano, si kuonyesha teknolojia kwa ajili ya teknolojia.

---

## 2. Mandhari na Tatizo

Tanzania ina historia na muundo wa kipekee — Muungano wa nchi mbili chini ya bendera moja. Hata hivyo, maswali muhimu bado yana changamoto kwa umma:

- Muungano ulianzishwa lini na kwa namna gani?
- Kwa nini kuna serikali mbili (Baraza la Mawaziri na Baraza la Mapinduzi)?
- "Mambo ya Muungano" (Union Matters) ni nini hasa?
- Tofauti kati ya mamlaka ya Bara na Zanzibar ni ipi?

**Changamoto kuu:**

| Tatizo | Athari |
|--------|--------|
| Nyaraka rasmi ni ndefu na ngumu | Vijana na raia wengi hawasomi Katiba kwa undani |
| Taarifa mtandaoni ni mchanganyiko | Ukweli, maoni, na uvumi vimechanganyika |
| Hakuna zana ya elimu inayopatikana | Elimu ya uraia inabaki darasani tu, si maisha ya kila siku |
| Lugha na mitindo tofauti | Kila mtu anajifunza tofauti — mfumo mmoja haufikii wote |

Hii inapunguza **uraia wenye maarifa** — uwezo wa kushiriki katika mazungumzo ya kitaifa kwa msingi wa ukweli, si mitindo tu.

---

## 3. Suluhisho: MuunganoAi

MuunganoAi ni **msaidizi wa mazungumzo** maalum wa elimu ya Muungano. Si chatbot ya jumla — ni zana iliyojengwa kwa ajili ya swali moja kuu: *"Nifundishe Muungano wangu."*

### Jinsi inavyofanya kazi

```
  Swali la mtumiaji (maandishi au sauti)
              │
              ▼
  ┌───────────────────────┐
  │  Utafutaji wa semantic │  ← ChromaDB + embeddings za lugha mbili
  └───────────────────────┘
              │
              ▼  Vipande 4–6 vinavyohusiana zaidi
  ┌───────────────────────┐
  │  AI ya mazungumzo      │  ← Gemini 2.5 Flash (OpenRouter)
  │  + muktadha wa vyanzo  │
  └───────────────────────┘
              │
              ▼
  Jibu la mazungumzo (maandishi / sauti)
  + marejeo ya vyanzo (mtindo rasmi)
```

### Sifa kuu

- **Vyanzo vilivyothibitishwa** — allowlist ya tovuti na nyaraka rasmi; blogi na maoni hayajumuishwi
- **Kipaumbele cha nyaraka** — Katiba na Articles of Union kwanza
- **Lugha mbili** — Kiswahili na Kiingereza, kubadilisha papo hapo
- **Mitindo 5 ya majibu** — youth, simple, student, official, default
- **Mazungumzo ya kawaida** — andika au zungumza; soma au sikiliza jibu
- **Streaming** — majibu yanakuja moja kwa moja, kama mazungumzo halisi

---

## 4. Teknolojia

| Tabaka | Teknolojia | Kazi |
|--------|------------|------|
| Backend | Python 3.10+, FastAPI | API, chat, ingest |
| Hifadhi ya maarifa | ChromaDB | Vector store ya vipande vya nyaraka |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 | Utafutaji wa semantic (SW/EN) |
| LLM | Gemini 2.5 Flash (OpenRouter) | Majibu ya mazungumzo |
| Crawler | Trafilatura + allowlist YAML | Kupakia vyanzo rasmi mtandaoni |
| Frontend | HTML, CSS, JavaScript | UI ya mazungumzo, hakuna framework |
| Sauti | Web Speech API | STT/TTS — sehemu ya kawaida ya UX |

**Kwa nini RAG?**  
Mfumo wa kawaida wa AI unaweza "kubuni" tarehe na ukweli. RAG inahakikisha kila jibu lina msingi wa nyaraka halisi — kanuni muhimu kwa elimu ya uraia na sheria.

---

## 5. Lengo na Watumiaji

**Watumiaji wa msingi:**
- Vijana (shule ya sekondari na vyuo)
- Wanafunzi wa Historia, Siasa, na Sheria
- Walimu wanaohitaji msaidizi wa kufafanua mambo magumu
- Raia wanaotaka kuelewa nchi yao bila kusoma PDF 300 ukurasa

**Matumizi ya kawaida:**
- "Muungano ulianzishwa lini?"
- "Mambo ya Muungano ni yapi?"
- "Kwa nini Tanzania ina serikali mbili?"
- "Nani alisaini Hati ya Muungano?"
- "Tofauti ya Bara na Zanzibar ni nini?"

---

## 6. Jinsi Tutakavyowafikia Vijana

Vijana hawataki PDF — wanataka majibu ya haraka, kwa lugha wanayoielewa, kwenye simu zao.

1. **Tovuti inayopatikana kwenye simu** — inafunguka moja kwa moja, hakuna usakinishaji
2. **Mitandao ya kijamii** — maswali mafupi + majibu ya MuunganoAi (Instagram, TikTok, WhatsApp)
3. **Shule na vyuo** — msaidizi wa walimu wa Historia na Uraia, si mbadala wa mtaala
4. **Vilabu vya TEHAMA** — kuonyesha AI inaweza kutumika kwa elimu ya uraia, si burudani tu

Tunazungumza lugha yao — Kiswahili kwanza, sentensi fupi, mifano halisi.

---

## 7. Athari Inayotarajiwa

### Kuongeza uelewa wa Muungano

MuunganoAi inabadilisha nyaraka ngumu kuwa **mazungumzo ya kawaida**, yenye msingi wa vyanzo. Mtumiaji anajifunza kwa kuuliza — njia ya asili ya kujifunza — badala ya kusoma kwa lazima.

**Matokeo yanayotarajiwa:**
- Vijana wanaelewa historia na muundo wa nchi yao
- Kupungua kwa uvumi na taarifa potofu mtandaoni
- Kuongezeka kwa mazungumzo ya kiufundi kuhusu Muungano
- Msingi bora wa uraia wenye maarifa

### SDGs zinazohusiana

| SDG | Uchanganuzi |
|-----|-------------|
| **4 — Elimu bora** | Elimu ya uraia inayopatikana, lugha mbili, mitindo mbalimbali |
| **16 — Amani na haki** | Uelewa wa taasisi za kitaifa na utawala wa sheria |
| **5 — Usawa wa kijinsia** | Wasichana katika TEHAMA wanajenga AI ya kuaminika kwa jamii |

### Makadirio ya Ufikiaji

| Kipindi | Lengo |
|---------|-------|
| Mwaka 1 | 5,000 – 10,000 vijana (tovuti, mitandao, shule 5–10) |
| Mwaka 2 | 50,000+ (ushirikiano na programu za TEHAMA za kitaifa) |
| Muda mrefu | Msaidizi wa kawaida wa kujifunza kuhusu Muungano wa Tanzania |

---

## 8. Hali ya Sasa na Mpango wa Utekelezaji

### Iliyokamilika (~90%)

- [x] Mfumo wa RAG kamili (retrieve → context → LLM)
- [x] Maktaba ya maarifa: 600+ vipande vya nyaraka rasmi
- [x] Ingest ya PDF, tovuti rasmi, na youth Q&A
- [x] Chat na streaming
- [x] Lugha mbili (SW/EN) na mitindo 5
- [x] UI ya mazungumzo (simu + desktop)
- [x] Uwezo wa sauti (ingizo na majibu)
- [x] API ya afya, mapendekezo, na ingest

### Inayobaki (~10%)

- [ ] Uboreshaji wa UI/UX
- [ ] Upanuzi wa vyanzo (makala zaidi, hotuba rasmi)
- [ ] Upimaji na watumiaji halisi (pilot shuleni)
- [ ] Uwekaji mtandaoni (hosting ya umma)

### Mpango wa Hatua (Roadmap)

| Mwezi | Hatua |
|-------|-------|
| 1 | Pilot na shule 2–3; kukusanya maoni |
| 2–3 | Uboreshaji kulingana na maoni; upanuzi wa vyanzo |
| 4–6 | Uzinduzi wa umma; ushirikiano na vilabu vya TEHAMA |
| 6–12 | Ushirikiano na wizara/taasisi za elimu; matengenezo endelevu |

---

## 9. Uaminifu na Kanuni

MuunganoAi **haibuni ukweli**. Kanuni za msingi:

1. Majibu yanategemea muktadha uliopatikana kutoka vyanzo vilivyoidhinishwa
2. Tarehe na ukweli maalum — kamwe si makisio ya modeli
3. Vyanzo visivyothibitishwa vimezuiwa kwenye allowlist
4. Mtindo rasmi unaonyesha marejeo ya nyaraka mwishoni
5. Hii ni **zana ya elimu** — haielekei ushauri wa kisheria wala haiwakilishi serikali yoyote

---

## 10. Timu

| Jina | Wajibu | Taasisi |
|------|--------|---------|
| *[Jaza jina]* | *[Mhusika / Developer / Lead]* | *[Chuo]* |
| *[Jaza jina]* | *[Mhusika]* | *[Chuo]* |

---

## 11. Mahitaji ya Msaada (Ikiwa Unahitajika)

| Kipengele | Maelezo |
|-----------|---------|
| **Mentorship** | AI ethics, RAG best practices, scaling |
| **Ushirikiano** | Wizara ya Elimu, TCRA, vilabu vya TEHAMA |
| **Hosting** | Server ya umma au Cloudflare Workers |
| **Ufikiaji** | Kuunganishwa na programu za TEHAMA za kitaifa |

---

## 12. Hitimisho

MuunganoAi inaonyesha jinsi **akili bandia inavyoweza kutumika kwa maendeleo halisi** — si burudani, si uvumi, bali **elimu ya uraia inayopatikana** kwa kizazi kinachokua na kidijitali.

Tunataka kila kijana wa Tanzania aelewe nchi yake — si kwa kusoma PDF, bali kwa kuuliza swali na kupata jibu la kuaminika.

> **MuunganoAi — elewa Muungano wako, kwa lugha yako, kutoka vyanzo unavyoweza kuamini.**

---

**Mawasiliano**  
*[Jaza: barua pepe, simu, GitHub, demo URL]*

---

*Hati hii ni sehemu ya ombi la Girls in ICT AI Hackathon 2026 — "Akili Unde kwa Maendeleo: Wasichana Wakibadilisha Mustakabali wa Kidijitali."*
