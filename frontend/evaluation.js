const runButton = document.getElementById("run-eval");
const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const resultsEl = document.getElementById("results");
const languageEl = document.getElementById("language");
const askForm = document.getElementById("ask-form");
const quickQuestionEl = document.getElementById("quick-question");
const quickStatusEl = document.getElementById("ask-status");
const quickAnswerEl = document.getElementById("quick-answer");
const quickSourcesEl = document.getElementById("quick-sources");
const quickChunksEl = document.getElementById("quick-chunks");
const quickChunkEl = document.getElementById("quick-chunk-count");
const quickEmbeddingEl = document.getElementById("quick-embedding-model");

let allResults = [];
let currentFilter = "all";

function clearResults() {
  summaryEl.textContent = "";
  resultsEl.textContent = "";
}

function createSummary(summary) {
  const wrapper = document.createElement("div");
  wrapper.className = "summary-grid";

  const items = [
    { label: "Total", value: summary.total, filter: "all" },
    { label: "Right", value: summary.right, filter: "right" },
    { label: "Middle", value: summary.middle, filter: "middle" },
    { label: "Wrong", value: summary.wrong, filter: "wrong" },
    { label: "Accuracy", value: `${(summary.accuracy * 100).toFixed(1)}%` },
  ];

  items.forEach((item) => {
    const itemEl = document.createElement("div");
    itemEl.className = "summary-item";
    const title = document.createElement("span");
    title.textContent = item.label;
    const val = document.createElement("strong");
    val.textContent = item.value;
    itemEl.appendChild(title);
    itemEl.appendChild(val);
    if (item.filter) {
      itemEl.classList.add("filter");
      itemEl.dataset.filter = item.filter;
      if (item.filter === currentFilter) {
        itemEl.classList.add("active");
      }
      itemEl.addEventListener("click", () => {
        currentFilter = item.filter || "all";
        renderFilteredResults();
      });
    }
    wrapper.appendChild(itemEl);
  });

  summaryEl.appendChild(wrapper);
}

function badgeClass(verdict) {
  const lower = verdict.toLowerCase();
  if (lower.startsWith("right")) return "right";
  if (lower.startsWith("middle")) return "middle";
  if (lower.startsWith("wrong")) return "wrong";
  return "middle";
}

function renderSources(sources) {
  const list = document.createElement("ul");
  list.className = "sources-list";

  sources.forEach((src) => {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.textContent = src;
    link.href = encodeURI(src);
    link.target = "_blank";
    link.rel = "noreferrer";
    item.appendChild(link);
    list.appendChild(item);
  });

  return list;
}

function renderResult(result, index) {
  const card = document.createElement("article");
  card.className = "result-card";

  const head = document.createElement("div");
  head.className = "result-head";
  const title = document.createElement("h3");
  title.textContent = `#${index + 1} ${result.question}`;
  const badge = document.createElement("span");
  badge.className = `badge ${badgeClass(result.verdict || "")}`;
  badge.textContent = result.verdict || "Unknown";
  head.appendChild(title);
  head.appendChild(badge);

  const expected = document.createElement("div");
  expected.className = "result-block";
  const expectedLabel = document.createElement("span");
  expectedLabel.textContent = "Expected";
  const expectedText = document.createElement("p");
  expectedText.textContent = result.expected || "";
  expected.appendChild(expectedLabel);
  expected.appendChild(expectedText);

  const answer = document.createElement("div");
  answer.className = "result-block";
  const answerLabel = document.createElement("span");
  answerLabel.textContent = "Answer";
  const answerText = document.createElement("p");
  answerText.textContent = result.answer || "";
  answer.appendChild(answerLabel);
  answer.appendChild(answerText);

  card.appendChild(head);
  card.appendChild(expected);
  card.appendChild(answer);

  if (Array.isArray(result.sources) && result.sources.length) {
    const sourcesBlock = document.createElement("div");
    sourcesBlock.className = "result-block";
    const sourcesLabel = document.createElement("span");
    sourcesLabel.textContent = "Sources";
    sourcesBlock.appendChild(sourcesLabel);
    sourcesBlock.appendChild(renderSources(result.sources));
    card.appendChild(sourcesBlock);
  }

  if (result.error) {
    const errorBlock = document.createElement("div");
    errorBlock.className = "result-block";
    const errorLabel = document.createElement("span");
    errorLabel.textContent = "Error";
    const errorText = document.createElement("p");
    errorText.textContent = result.error;
    errorBlock.appendChild(errorLabel);
    errorBlock.appendChild(errorText);
    card.appendChild(errorBlock);
  }

  if (Array.isArray(result.chunks) && result.chunks.length) {
    const details = document.createElement("details");
    details.className = "details";
    const summary = document.createElement("summary");
    summary.textContent = `Retrieved chunks (${result.chunks.length})`;
    details.appendChild(summary);

    result.chunks.forEach((chunk) => {
      const chunkEl = document.createElement("div");
      chunkEl.className = "chunk";

      const meta = document.createElement("div");
      meta.className = "chunk-meta";
      const score = chunk.score !== undefined ? chunk.score.toFixed(4) : "n/a";
      meta.textContent = `source: ${chunk.source || "unknown"} | score: ${score} | chunk: ${chunk.chunk_index}`;

      const text = document.createElement("p");
      text.textContent = chunk.text || "";

      chunkEl.appendChild(meta);
      chunkEl.appendChild(text);
      details.appendChild(chunkEl);
    });

    card.appendChild(details);
  }

  return card;
}

function renderFilteredResults() {
  resultsEl.textContent = "";
  const filtered = allResults.filter((result) => {
    if (currentFilter === "all") return true;
    return (result.verdict || "").toLowerCase().startsWith(currentFilter);
  });

  filtered.forEach((result, index) => {
    resultsEl.appendChild(renderResult(result, index));
  });

  const cards = summaryEl.querySelectorAll(".summary-item.filter");
  cards.forEach((card) => {
    card.classList.toggle("active", card.dataset.filter === currentFilter);
  });
}

async function runEvaluation() {
  clearResults();
  statusEl.textContent = "Running...";
  runButton.disabled = true;

  try {
    const res = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: languageEl.value }),
    });

    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }

    const data = await res.json();
    if (!data || !data.summary) {
      throw new Error("Invalid response");
    }

    allResults = data.results || [];
    currentFilter = "all";
    createSummary(data.summary);
    renderFilteredResults();

    statusEl.textContent = "Done";
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  } finally {
    runButton.disabled = false;
  }
}

function renderQuickSources(sources) {
  quickSourcesEl.textContent = "";
  if (!Array.isArray(sources) || sources.length === 0) {
    return;
  }
  const label = document.createElement("span");
  label.textContent = "Sources";
  quickSourcesEl.appendChild(label);
  quickSourcesEl.appendChild(renderSources(sources));
}

function renderQuickChunks(chunks) {
  quickChunksEl.textContent = "";
  const summary = document.createElement("summary");
  summary.textContent = `Retrieved chunks (${chunks.length || 0})`;
  quickChunksEl.appendChild(summary);

  if (!Array.isArray(chunks) || chunks.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No chunks returned.";
    quickChunksEl.appendChild(empty);
    return;
  }

  chunks.forEach((chunk) => {
    const chunkEl = document.createElement("div");
    chunkEl.className = "chunk";

    const meta = document.createElement("div");
    meta.className = "chunk-meta";
    const score = chunk.score !== undefined ? chunk.score.toFixed(4) : "n/a";
    meta.textContent = `source: ${chunk.source || "unknown"} | score: ${score} | chunk: ${chunk.chunk_index}`;

    const text = document.createElement("p");
    text.textContent = chunk.text || "";

    chunkEl.appendChild(meta);
    chunkEl.appendChild(text);
    quickChunksEl.appendChild(chunkEl);
  });
}

async function runQuickAsk(question) {
  quickStatusEl.textContent = "Thinking...";
  quickAnswerEl.textContent = "";
  renderQuickSources([]);
  renderQuickChunks([]);

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        k: Number(quickChunkEl.value),
        embedding_model: quickEmbeddingEl.value,
      }),
    });

    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }

    const data = await res.json();
    quickAnswerEl.textContent = data.answer || "No response.";
    renderQuickSources(data.sources || []);
    renderQuickChunks(data.chunks || []);
    quickStatusEl.textContent = "Done";
  } catch (err) {
    quickAnswerEl.textContent = `Error: ${err.message}`;
    quickStatusEl.textContent = "Error";
  }
}

runButton.addEventListener("click", runEvaluation);

askForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const q = quickQuestionEl.value.trim();
  if (!q) {
    quickStatusEl.textContent = "Idle";
    return;
  }
  runQuickAsk(q);
});
