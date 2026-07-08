const API_BASE = "http://127.0.0.1:8000";

const form = document.getElementById("new-task-form");
const titleInput = document.getElementById("title");
const list = document.getElementById("task-list");
const emptyMessage = document.getElementById("empty");
const errorMessage = document.getElementById("error");

let tasks = [];

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

function showError(error) {
  errorMessage.textContent = `${error.message}. Is the API running on ${API_BASE}?`;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.hidden = true;
}

function render() {
  list.replaceChildren();
  emptyMessage.hidden = tasks.length > 0;

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

    item.append(label, remove);
    list.append(item);
  }
}

async function loadTasks() {
  try {
    tasks = await api("/tasks");
    clearError();
  } catch (error) {
    showError(error);
  }
  render();
}

async function addTask(title) {
  const created = await api("/tasks", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
  tasks.push(created);
}

async function toggleTask(task) {
  try {
    const updated = await api(`/tasks/${task.id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed: !task.completed }),
    });
    tasks = tasks.map((item) => (item.id === updated.id ? updated : item));
    clearError();
  } catch (error) {
    showError(error);
  }
  // Always re-render: on failure this snaps the checkbox back to server state.
  render();
}

async function deleteTask(task) {
  try {
    await api(`/tasks/${task.id}`, { method: "DELETE" });
    tasks = tasks.filter((item) => item.id !== task.id);
    clearError();
  } catch (error) {
    showError(error);
  }
  render();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = titleInput.value.trim();
  if (!title) return;

  try {
    await addTask(title);
    titleInput.value = "";
    clearError();
  } catch (error) {
    showError(error);
  }
  render();
});

loadTasks();
