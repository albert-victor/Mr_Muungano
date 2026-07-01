/**
 * Rich markdown formatter for chat responses
 */

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatInline(text) {
  let s = escapeHtml(text);
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/\*(.+?)\*/g, "<em>$1</em>");
  s = s.replace(/`(.+?)`/g, '<code class="md-code">$1</code>');
  // Highlight dates (e.g. 26 Aprili 1964, April 26, 1964, 1964)
  s = s.replace(
    /\b(\d{1,2}\s+(?:Januari|Februari|Machi|Aprili|Mei|Juni|Julai|Agosti|Septemba|Oktoba|Novemba|Desemba|April|January|February|March|May|June|July|August|September|October|November|December)\s+\d{4})\b/gi,
    '<span class="md-date">$1</span>'
  );
  s = s.replace(/\b((?:19|20)\d{2})\b/g, '<span class="md-year">$1</span>');
  return s;
}

function isSourcesHeading(line) {
  const t = line.trim().replace(/^\*\*|\*\*$/g, "").replace(/:$/, "").toLowerCase();
  return ["vyanzo", "sources", "chanzo", "reference", "references", "marejeo"].includes(t);
}

export function formatStreaming(text) {
  if (!text) return "";
  const safe = escapeHtml(text).replace(/\n/g, "<br>");
  return `<div class="md-content md-content--streaming"><p class="md-p">${safe}</p></div>`;
}

export function formatMarkdown(text) {
  if (!text) return "";

  const lines = text.split("\n");
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      i++;
      continue;
    }

    // Sources section heading
    if (isSourcesHeading(trimmed)) {
      const items = [];
      i++;
      while (i < lines.length) {
        const sl = lines[i].trim();
        if (!sl) { i++; continue; }
        if (/^#{1,3}\s/.test(sl) || isSourcesHeading(sl)) break;
        if (/^[-•*]\s/.test(sl) || /^\d+[.)]\s/.test(sl)) {
          items.push(sl.replace(/^[-•*]\s|^\d+[.)]\s/, ""));
          i++;
        } else if (items.length && !/^[-•*\d]/.test(sl)) {
          items[items.length - 1] += " " + sl;
          i++;
        } else break;
      }
      blocks.push(
        `<div class="md-sources">
          <div class="md-sources__head"><i class="fa-solid fa-bookmark"></i> ${formatInline(trimmed.replace(/:$/, ""))}</div>
          <ul class="md-ul md-ul--sources">${items.map((it) => `<li class="md-li"><span class="md-li__text">${formatInline(it)}</span></li>`).join("")}</ul>
        </div>`
      );
      continue;
    }

    // Headers
    if (/^###\s/.test(trimmed)) {
      blocks.push(`<h4 class="md-h3">${formatInline(trimmed.slice(4))}</h4>`);
      i++;
      continue;
    }
    if (/^##\s/.test(trimmed)) {
      blocks.push(`<h3 class="md-h2">${formatInline(trimmed.slice(3))}</h3>`);
      i++;
      continue;
    }
    if (/^#\s/.test(trimmed)) {
      blocks.push(`<h2 class="md-h1">${formatInline(trimmed.slice(2))}</h2>`);
      i++;
      continue;
    }

    // Blockquote
    if (/^>\s/.test(trimmed)) {
      const quoteLines = [];
      while (i < lines.length && /^>\s?/.test(lines[i].trim() || ">")) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ""));
        i++;
      }
      blocks.push(`<blockquote class="md-quote">${quoteLines.map((q) => `<p>${formatInline(q)}</p>`).join("")}</blockquote>`);
      continue;
    }

    // Unordered list
    if (/^[-•*]\s/.test(trimmed)) {
      const items = [];
      while (i < lines.length && /^[-•*]\s/.test(lines[i].trim())) {
        const raw = lines[i].trim().replace(/^[-•*]\s+/, "").replace(/^•\s*/, "");
        items.push(raw);
        i++;
      }
      blocks.push(
        `<ul class="md-ul">${items
          .map((it) => `<li class="md-li"><span class="md-li__text">${formatInline(it)}</span></li>`)
          .join("")}</ul>`
      );
      continue;
    }

    // Ordered list
    if (/^\d+[.)]\s/.test(trimmed)) {
      const items = [];
      while (i < lines.length && /^\d+[.)]\s/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^\d+[.)]\s/, ""));
        i++;
      }
      blocks.push(`<ol class="md-ol">${items.map((it) => `<li class="md-li"><span class="md-li__text">${formatInline(it)}</span></li>`).join("")}</ol>`);
      continue;
    }

    // Paragraph (collect consecutive non-empty lines)
    const paraLines = [];
    while (i < lines.length) {
      const pl = lines[i].trim();
      if (!pl) break;
      if (/^#{1,3}\s|^[-•*]\s|^\d+[.)]\s|^>\s/.test(pl) || isSourcesHeading(pl)) break;
      if (isSourcesHeading(pl)) break;
      paraLines.push(pl);
      i++;
    }
    if (paraLines.length) {
      blocks.push(`<p class="md-p">${formatInline(paraLines.join(" "))}</p>`);
    }
  }

  return `<div class="md-content">${blocks.join("")}</div>`;
}

export function escapeAttr(str) {
  return escapeHtml(str).replace(/'/g, "&#39;");
}

export { escapeHtml };
