const form = document.getElementById("ask-form");
const questionEl = document.getElementById("question");
const statusEl = document.getElementById("status");
const chatEl = document.getElementById("chat");

function addMessage(role, text) {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.textContent = text;
  chatEl.appendChild(message);
  chatEl.scrollTop = chatEl.scrollHeight;
  return message;
}

function addSources(target, sources) {
  if (!Array.isArray(sources) || sources.length === 0) {
    return;
  }

  const container = document.createElement("div");
  container.className = "sources";

  const title = document.createElement("div");
  title.className = "sources-title";
  title.textContent = "Sources";
  container.appendChild(title);

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

  container.appendChild(list);
  target.appendChild(container);
}

async function ask(question) {
  statusEl.textContent = "Thinking...";
  const botMessage = addMessage("bot", "Thinking...");

  try {
    const res = await fetch("/rag/invoke", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: question }),
    });

    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }

    const data = await res.json();
    const output = data.output ?? { answer: "No response.", sources: [] };
    const answer = output.answer ?? "No response.";
    const sources = output.sources ?? [];
    botMessage.textContent = answer;
    addSources(botMessage, sources);
    statusEl.textContent = "Done";
  } catch (err) {
    botMessage.textContent = `Error: ${err.message}`;
    statusEl.textContent = "Error";
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const q = questionEl.value.trim();
  if (!q) {
    statusEl.textContent = "Idle";
    return;
  }
  addMessage("user", q);
  questionEl.value = "";
  ask(q);
});
