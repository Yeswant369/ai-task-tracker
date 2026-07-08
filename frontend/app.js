const API_BASE = "http://127.0.0.1:8000";
const PRIORITIES = ["high", "medium", "low"];

const form = document.getElementById("new-task-form");
const titleInput = document.getElementById("title");
const newPriority = document.getElementById("new-priority");
const filterSelect = document.getElementById("filter");
const sortCheckbox = document.getElementById("sort");
const list = document.getElementById("task-list");
const emptyMessage = document.getElementById("empty");
const errorMessage = document.getElementById("error");
const statusBar = document.getElementById("status-bar");
const themeToggle = document.getElementById("theme-toggle");

// `tasks` is what the server returned for the current filter/sort.
// `allTasks` is every task, so the status bar can report real totals.
let tasks = [];
let allTasks = [];

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`${options.method ?? "GET"} ${path} failed (${response.status})`);
  }

  // 204 No Content has no body to parse.
  return response.status === 204 ? null : response.json();
}

function buildQuery() {
  const params = new URLSearchParams();
  if (filterSelect.value !== "all") params.set("priority", filterSelect.value);
  if (sortCheckbox.checked) params.set("sort", "priority");

  const query = params.toString();
  return query ? `?${query}` : "";
}

function showError(error) {
  errorMessage.textContent = `${error.message}. Is the API running on ${API_BASE}?`;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.hidden = true;
}

function renderStatusBar() {
  const total = allTasks.length;

  if (total === 0) {
    statusBar.textContent = "";
    return;
  }

  const completed = allTasks.filter((task) => task.completed).length;
  const remaining = total - completed;
  const filtered = tasks.length !== total ? ` — showing ${tasks.length}` : "";

  statusBar.textContent = `${total} total · ${completed} completed · ${remaining} remaining${filtered}`;
}

function buildPrioritySelect(task) {
  const select = document.createElement("select");
  select.className = `priority priority-${task.priority}`;
  select.setAttribute("aria-label", `Priority for "${task.title}"`);

  for (const value of PRIORITIES) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value[0].toUpperCase() + value.slice(1);
    option.selected = value === task.priority;
    select.append(option);
  }

  select.addEventListener("change", () => changePriority(task, select.value));
  return select;
}

function render() {
  list.replaceChildren();

  emptyMessage.hidden = tasks.length > 0;
  emptyMessage.textContent =
    allTasks.length === 0
      ? "No tasks yet. Add one above."
      : "No tasks match this filter.";

  for (const task of tasks) {
    const item = document.createElement("li");
    item.className = task.completed ? "task done" : "task";

    const label = document.createElement("label");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.completed;
    checkbox.addEventListener("change", () => toggleTask(task));

    const text = document.createElement("span");
    // textContent, not innerHTML: titles are user input.
    text.textContent = task.title;

    label.append(checkbox, text);

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "delete";
    remove.textContent = "Delete";
    remove.setAttribute("aria-label", `Delete "${task.title}"`);
    remove.addEventListener("click", () => deleteTask(task));

    const actions = document.createElement("div");
    actions.className = "actions";
    actions.append(buildPrioritySelect(task), remove);

    item.append(label, actions);
    list.append(item);
  }

  renderStatusBar();
}

async function loadTasks() {
  try {
    const query = buildQuery();
    // Only fetch the unfiltered list separately when a query is actually applied.
    const [visible, everything] = await Promise.all([
      api(`/tasks${query}`),
      query ? api("/tasks") : null,
    ]);

    tasks = visible;
    allTasks = everything ?? visible;
    clearError();
  } catch (error) {
    showError(error);
  }
  render();
}

// Every mutation re-reads from the server. A purely local edit could otherwise
// leave a task on screen that no longer matches the active filter (for example,
// changing a task's priority while filtering by "high").
// Returns true when the request succeeded, so callers can avoid destructive UI
// updates (like clearing the input) after a failure.
async function mutate(request) {
  try {
    await request();
    clearError();
  } catch (error) {
    showError(error);
    render(); // snap the UI back to the last known server state
    return false;
  }
  await loadTasks();
  return true;
}

const addTask = (title, priority) =>
  mutate(() =>
    api("/tasks", { method: "POST", body: JSON.stringify({ title, priority }) })
  );

const toggleTask = (task) =>
  mutate(() =>
    api(`/tasks/${task.id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed: !task.completed }),
    })
  );

const changePriority = (task, priority) =>
  mutate(() =>
    api(`/tasks/${task.id}`, {
      method: "PATCH",
      body: JSON.stringify({ priority }),
    })
  );

const deleteTask = (task) =>
  mutate(() => api(`/tasks/${task.id}`, { method: "DELETE" }));

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = titleInput.value.trim();
  if (!title) return;

  // Keep the typed title on screen if the request failed.
  if (await addTask(title, newPriority.value)) {
    titleInput.value = "";
  }
  titleInput.focus();
});

filterSelect.addEventListener("change", loadTasks);
sortCheckbox.addEventListener("change", loadTasks);

// --- Bonus: dark mode --------------------------------------------------------

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeToggle.textContent = theme === "dark" ? "Light mode" : "Dark mode";
  themeToggle.setAttribute("aria-pressed", String(theme === "dark"));
}

function initialTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "dark" || saved === "light") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

themeToggle.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
});

applyTheme(initialTheme());
loadTasks();
