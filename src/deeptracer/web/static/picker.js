function formatWhen(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function cloneTemplate(id) {
  const template = document.getElementById(id);
  return template.content.firstElementChild.cloneNode(true);
}

function renderEmpty() {
  return cloneTemplate("tpl-empty");
}

function renderTable(sessions) {
  const root = cloneTemplate("tpl-list");
  root.querySelector(".count").textContent = String(sessions.length);
  const body = root.querySelector("tbody");
  for (const session of sessions) {
    const row = document.getElementById("tpl-row").content.firstElementChild.cloneNode(
      true,
    );
    row.querySelector(".id").textContent = session.session_id;
    row.querySelector(".project").textContent = session.project_label;
    row.querySelector(".path").textContent = session.log_path;
    row.querySelector(".when").textContent = formatWhen(session.modified_at);
    row.querySelector(".size").textContent = formatSize(session.size_bytes);
    body.appendChild(row);
  }
  return root;
}

function show(node) {
  const root = document.getElementById("root");
  root.className = "";
  root.replaceChildren(node);
}

fetch("/api/sessions")
  .then((res) => {
    if (!res.ok) throw new Error("HTTP " + res.status);
    return res.json();
  })
  .then((data) => {
    const sessions = data.sessions || [];
    show(sessions.length ? renderTable(sessions) : renderEmpty());
  })
  .catch((err) => {
    const message = document.createElement("p");
    message.className = "error";
    message.textContent = "Could not load sessions: " + err.message;
    show(message);
  });
