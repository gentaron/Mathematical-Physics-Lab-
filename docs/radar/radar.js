// Frontier Radar — client-side search over radar.json.
// Security: no innerHTML / eval / inline handlers; every value is set with textContent;
// links are re-checked (absolute http/https only) before they reach an href.
(() => {
  "use strict";
  const form = document.getElementById("search");
  const input = document.getElementById("q");
  const list = document.getElementById("results") || createList();
  const status = document.getElementById("status");
  const chips = Array.from(document.querySelectorAll(".chip"));
  const all = document.getElementById("all");
  const MONTH = /^\d{4}-\d{2}\.json$/;
  let archiveLoaded = false;
  const LIMIT = 120;
  let radar = null;
  const active = new Set();

  function createList() {
    const ol = document.createElement("ol");
    ol.id = "results";
    ol.className = "items";
    const empty = document.querySelector(".empty");
    (empty ? empty.parentNode : document.querySelector("main")).appendChild(ol);
    return ol;
  }

  const halfLife = () => (radar && radar.ranking && radar.ranking.half_life_days) || 14;
  const rankOf = (item, now) => (Number(item.score) || 0) * Math.pow(0.5, Math.max(0, now - Date.parse(item.date)) / 86400e3 / halfLife());
  function resort() {
    const now = Date.now();
    for (const item of radar.items) item.rank = rankOf(item, now);
    radar.items.sort((a, b) => b.rank - a.rank);
  }

  const fold = (s) => String(s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();

  function safeUrl(value) {
    try {
      const url = new URL(String(value));
      return (url.protocol === "https:" || url.protocol === "http:") && !url.username && !url.password ? url.href : null;
    } catch (_) {
      return null;
    }
  }

  function parseQuery(query) {
    const terms = [];
    const re = /(-?)(?:(\w+):)?(?:"([^"]+)"|(\S+))/g;
    let m;
    const alias = { t: "topic", source: "src", author: "au" };
    const known = new Set(["", "topic", "t", "src", "source", "au", "author", "tier", "since"]);
    while ((m = re.exec(String(query).slice(0, 200))) !== null) {
      let field = (m[2] || "").toLowerCase();
      let value = m[3] || m[4] || "";
      if (!known.has(field)) { value = field + ":" + value; field = ""; }
      terms.push({ negate: m[1] === "-", field: alias[field] || field, value: fold(value) });
    }
    return terms;
  }

  function since(item, value, now) {
    const when = Date.parse(item.date);
    const m = /^(\d{1,4})([dhw])$/.exec(value);
    if (m) {
      const unit = { h: 3600e3, d: 86400e3, w: 7 * 86400e3 }[m[2]];
      return when >= now - Number(m[1]) * unit;
    }
    const start = Date.parse(value);
    return !Number.isNaN(start) && when >= start;
  }

  function matches(item, terms, now) {
    const hay = fold([item.title, item.summary, (item.authors || []).join(" "), (item.categories || []).join(" "),
      item.arxiv || "", item.doi || ""].join(" "));
    for (const t of terms) {
      let hit;
      if (t.field === "topic") hit = (item.topics || []).some((x) => fold(x).includes(t.value));
      else if (t.field === "src") hit = [...(item.sources || []), ...(item.source_names || [])].some((x) => fold(x).includes(t.value));
      else if (t.field === "au") hit = fold((item.authors || []).join(" ")).includes(t.value);
      else if (t.field === "tier") hit = /^\d$/.test(t.value) && (item.tier || 3) <= Number(t.value);
      else if (t.field === "since") hit = since(item, t.value, now);
      else hit = hay.includes(t.value);
      if (hit === t.negate) return false;
    }
    if (active.size && !(item.topics || []).some((x) => active.has(x))) return false;
    return true;
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function render(items) {
    const labels = Object.fromEntries((radar.topics || []).map((t) => [t.id, t.label]));
    const fragment = document.createDocumentFragment();
    for (const item of items) {
      const href = safeUrl(item.url);
      if (!href) continue;
      const li = el("li", "item");
      const article = el("article");
      const h3 = el("h3");
      const a = el("a", "", item.title);
      a.href = href;
      a.rel = "noopener noreferrer nofollow";
      a.target = "_blank";
      h3.appendChild(a);
      article.appendChild(h3);
      const meta = el("p", "meta");
      const time = el("time", "", String(item.date).slice(0, 10));
      time.dateTime = item.date;
      const venue = item.venue ? [item.venue] : [];
      const cited = item.cited_by ? " · 被引用 " + item.cited_by : "";
      meta.append(time, " · " + [...venue, ...(item.source_names || [])].join(" / ") + " · score " + item.score + cited);
      article.appendChild(meta);
      if ((item.authors || []).length) {
        const more = item.authors.length > 5 ? " ほか" : "";
        article.appendChild(el("p", "authors", item.authors.slice(0, 5).join(", ") + more));
      }
      if (item.summary) article.appendChild(el("p", "summary", item.summary));
      const tags = el("p", "tags");
      for (const id of item.topics || []) tags.appendChild(el("span", "tag", labels[id] || id));
      article.appendChild(tags);
      if ((item.why || []).length) {
        const details = el("details", "why");
        details.appendChild(el("summary", "", "順位の理由"));
        const ul = el("ul");
        for (const reason of item.why) ul.appendChild(el("li", "", reason));
        details.appendChild(ul);
        article.appendChild(details);
      }
      li.appendChild(article);
      fragment.appendChild(li);
    }
    list.replaceChildren(fragment);
  }

  function update() {
    if (!radar) return;
    const query = input.value.trim();
    const terms = parseQuery(query);
    const now = Date.now();
    const found = radar.items.filter((item) => matches(item, terms, now));
    render(found.slice(0, LIMIT));
    status.textContent = `${found.length.toLocaleString()} 件${found.length > LIMIT ? `（上位 ${LIMIT} 件を表示）` : ""}`;
    const params = new URLSearchParams();
    if (query) params.set("q", query);
    if (active.size) params.set("topic", [...active].join(","));
    const next = params.toString() ? "?" + params.toString() : location.pathname;
    history.replaceState(null, "", next);
  }

  let timer = 0;
  input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(update, 120); });
  form.addEventListener("submit", (event) => { event.preventDefault(); update(); });
  for (const chip of chips) {
    chip.addEventListener("click", () => {
      const id = chip.dataset.topic;
      if (active.has(id)) active.delete(id); else active.add(id);
      chip.setAttribute("aria-pressed", String(active.has(id)));
      update();
    });
  }

  const params = new URLSearchParams(location.search);
  input.value = (params.get("q") || "").slice(0, 200);
  for (const id of (params.get("topic") || "").split(",").filter(Boolean)) {
    const chip = chips.find((c) => c.dataset.topic === id);
    if (chip) { active.add(id); chip.setAttribute("aria-pressed", "true"); }
  }

  async function loadArchive() {
    if (archiveLoaded || !radar) return;
    archiveLoaded = true;
    const seen = new Set(radar.items.map((item) => item.id));
    try {
      const index = await (await fetch("archive/index.json", { credentials: "omit", cache: "no-cache" })).json();
      const months = (index && Array.isArray(index.months) ? index.months : []).filter((m) => m && MONTH.test(m.file));
      let done = 0;
      for (const month of months) {
        const response = await fetch("archive/" + month.file, { credentials: "omit", cache: "no-cache" });
        if (!response.ok) continue;
        const shard = await response.json();
        for (const item of shard && Array.isArray(shard.items) ? shard.items : []) {
          if (item && !seen.has(item.id) && safeUrl(item.url)) { seen.add(item.id); radar.items.push(item); }
        }
        done += 1;
        status.textContent = `アーカイブ読み込み中 ${done}/${months.length} か月 · ${radar.items.length.toLocaleString()} 件`;
        if (done % 6 === 0 || done === months.length) { resort(); update(); }
      }
    } catch (_) {
      status.textContent = "アーカイブの一部を読み込めませんでした";
    }
    resort();
    update();
  }

  if (all) all.addEventListener("change", () => { if (all.checked) loadArchive(); });

  fetch("radar.json", { credentials: "omit", cache: "no-cache" })
    .then((response) => {
      if (!response.ok) throw new Error(String(response.status));
      return response.json();
    })
    .then((data) => {
      if (!data || data.schema !== "deeptech.radar/1" || !Array.isArray(data.items)) throw new Error("schema");
      radar = data;
      resort();
      status.textContent = `${data.items.length.toLocaleString()} 件を検索できます（全期間は「アーカイブも検索」）`;
      if (input.value || active.size) update();
    })
    .catch(() => { status.textContent = "検索データを読み込めませんでした（一覧は表示されています）"; });
})();
