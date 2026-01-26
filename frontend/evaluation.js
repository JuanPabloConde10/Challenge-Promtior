const runButton = document.getElementById("run-eval");
const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const resultsEl = document.getElementById("results");
const languageEl = document.getElementById("language");

function clearResults() {
  summaryEl.textContent = "";
  resultsEl.textContent = "";
}

function createSummary(summary) {
  const wrapper = document.createElement("div");
  wrapper.className = "summary-grid";

  const items = [
    ["Total", summary.total],
    ["Right", summary.right],
    ["Middle", summary.middle],
    ["Wrong", summary.wrong],
    ["Accuracy", `${(summary.accuracy * 100).toFixed(1)}%`],
  ];

  items.forEach(([label, value]) => {
    const item = document.createElement("div");
    item.className = "summary-item";
    const title = document.createElement("span");
    title.textContent = label;
    const val = document.createElement("strong");
    val.textContent = value;
    item.appendChild(title);
    item.appendChild(val);
    wrapper.appendChild(item);
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

    createSummary(data.summary);
    data.results.forEach((result, index) => {
      resultsEl.appendChild(renderResult(result, index));
    });

    statusEl.textContent = "Done";
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  } finally {
    runButton.disabled = false;
  }
}

runButton.addEventListener("click", runEvaluation);
