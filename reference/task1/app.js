"use strict";

const tasks = [];
let nextTaskId = 1;
let activeFilter = "all";

const taskForm = document.querySelector("#task-form");
const taskInput = document.querySelector("#task-input");
const taskList = document.querySelector("#task-list");
const formMessage = document.querySelector("#form-message");
const emptyState = document.querySelector("#empty-state");
const filterButtons = document.querySelectorAll(".filter-button");

taskForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const taskName = taskInput.value.trim();

  if (!taskName) {
    showMessage("請輸入任務內容。", true);
    taskInput.focus();
    return;
  }

  tasks.push({ id: nextTaskId, name: taskName, completed: false });
  nextTaskId += 1;
  taskForm.reset();
  showMessage("任務已新增。", false);
  renderTasks();
  taskInput.focus();
});

taskList.addEventListener("change", (event) => {
  const checkbox = event.target.closest('input[type="checkbox"][data-task-id]');
  if (!checkbox) return;

  const taskId = Number(checkbox.dataset.taskId);
  const task = tasks.find((item) => item.id === taskId);
  if (!task) return;

  task.completed = checkbox.checked;
  renderTasks({ type: "checkbox", id: taskId });
});

taskList.addEventListener("click", (event) => {
  const deleteButton = event.target.closest(".delete-button[data-task-id]");
  if (!deleteButton) return;

  const taskId = Number(deleteButton.dataset.taskId);
  const visibleIds = getVisibleTasks().map((task) => task.id);
  const deletedIndex = visibleIds.indexOf(taskId);
  const taskIndex = tasks.findIndex((task) => task.id === taskId);
  if (taskIndex === -1) return;

  tasks.splice(taskIndex, 1);
  const nextFocusId = visibleIds[deletedIndex + 1] ?? visibleIds[deletedIndex - 1];
  showMessage("任務已刪除。", false);
  renderTasks(nextFocusId ? { type: "delete", id: nextFocusId } : null);
  if (!nextFocusId) taskInput.focus();
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach((item) => {
      item.setAttribute("aria-pressed", String(item === button));
    });
    renderTasks();
  });
});

function getVisibleTasks() {
  if (activeFilter === "pending") return tasks.filter((task) => !task.completed);
  if (activeFilter === "completed") return tasks.filter((task) => task.completed);
  return tasks;
}

function renderTasks(focusTarget = null) {
  taskList.replaceChildren();
  const visibleTasks = getVisibleTasks();

  visibleTasks.forEach((task) => {
    const item = document.createElement("li");
    item.className = `task-item${task.completed ? " completed" : ""}`;

    const label = document.createElement("label");
    label.className = "task-check";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.completed;
    checkbox.dataset.taskId = task.id;
    checkbox.setAttribute("aria-label", `切換任務完成狀態：${task.name}`);

    const name = document.createElement("span");
    name.className = "task-name";
    name.textContent = task.name;

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-button";
    deleteButton.type = "button";
    deleteButton.dataset.taskId = task.id;
    deleteButton.textContent = "刪除";
    deleteButton.setAttribute("aria-label", `刪除任務：${task.name}`);

    label.append(checkbox, name);
    item.append(label, deleteButton);
    taskList.append(item);
  });

  updateSummary(visibleTasks.length);
  restoreTaskFocus(focusTarget);
}

function updateSummary(visibleCount) {
  const completedCount = tasks.filter((task) => task.completed).length;
  document.querySelector("#total-count").textContent = tasks.length;
  document.querySelector("#pending-count").textContent = tasks.length - completedCount;
  document.querySelector("#completed-count").textContent = completedCount;

  emptyState.hidden = visibleCount > 0;
  emptyState.textContent = "目前沒有任務";
}

function restoreTaskFocus(focusTarget) {
  if (!focusTarget) return;
  const selector = focusTarget.type === "checkbox"
    ? `input[data-task-id="${focusTarget.id}"]`
    : `.delete-button[data-task-id="${focusTarget.id}"]`;
  const target = taskList.querySelector(selector);
  (target ?? taskInput).focus();
}

function showMessage(message, isError) {
  formMessage.textContent = message;
  formMessage.classList.toggle("error", isError);
}

renderTasks();
