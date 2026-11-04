"use strict";

const express = require("express");
const path = require("node:path");

// 每次建立 app 都有獨立陣列；正式伺服器只建立一次，測試可各自隔離。
function createApp() {
  const app = express();
  const tasks = [];
  let nextTaskId = 1;
  const filterLabels = { all: "全部", pending: "未完成", completed: "已完成" };

  app.disable("x-powered-by");
  app.set("view engine", "ejs");
  app.set("views", path.join(__dirname, "views"));
  // HTML 表單以 application/x-www-form-urlencoded 傳送；解析後放在 req.body。
  app.use(express.urlencoded({ extended: false, limit: "10kb" }));
  app.use(express.static(path.join(__dirname, "public")));

  function getFilter(value) {
    return typeof value === "string" && Object.hasOwn(filterLabels, value) ? value : "all";
  }

  function renderPage(res, filter, message = "", isError = false, status = 200, input = "") {
    const visibleTasks = tasks.filter((task) => filter === "all"
      || (filter === "completed" ? task.completed : !task.completed));
    const completedCount = tasks.filter((task) => task.completed).length;
    res.set("Cache-Control", "no-store");
    return res.status(status).render("index", {
      tasks: visibleTasks, filter, filterLabels, message, isError, input,
      total: tasks.length, completedCount, pendingCount: tasks.length - completedCount
    });
  }

  function redirectToList(res, filter, message) {
    // Post/Redirect/Get：重新整理會重送 GET，不會再次新增或刪除。
    res.redirect(303, `/?${new URLSearchParams({ filter, message })}`);
  }

  function findTask(id) {
    if (!/^[1-9]\d*$/.test(id)) return undefined;
    return tasks.find((task) => task.id === Number(id));
  }

  app.get("/", (req, res) => {
    const messages = { added: "任務已新增。", updated: "完成狀態已更新。", deleted: "任務已刪除。" };
    const message = typeof req.query.message === "string" && Object.hasOwn(messages, req.query.message)
      ? messages[req.query.message] : "";
    renderPage(res, getFilter(req.query.filter), message);
  });

  app.post("/tasks", (req, res) => {
    const filter = getFilter(req.body.filter);
    const name = typeof req.body.name === "string" ? req.body.name.trim() : "";
    if (!name) return renderPage(res, filter, "請輸入任務內容。", true, 400);
    if (name.length > 200) return renderPage(res, filter, "任務名稱請勿超過 200 字元。", true, 400, name);
    tasks.push({ id: nextTaskId++, name, completed: false });
    redirectToList(res, filter, "added");
  });

  app.post("/tasks/:id/update", (req, res) => {
    const filter = getFilter(req.body.filter);
    const task = findTask(req.params.id);
    if (!task) return renderPage(res, filter, "找不到指定任務，資料可能已被刪除。", true, 404);
    // 未勾選 checkbox 不會傳送 completed；明確設定狀態，不使用反轉，重送仍一致。
    task.completed = req.body.completed === "on";
    redirectToList(res, filter, "updated");
  });

  app.post("/tasks/:id/delete", (req, res) => {
    const filter = getFilter(req.body.filter);
    const task = findTask(req.params.id);
    if (!task) return renderPage(res, filter, "找不到指定任務，資料可能已被刪除。", true, 404);
    tasks.splice(tasks.findIndex((item) => item.id === task.id), 1);
    redirectToList(res, filter, "deleted");
  });

  app.use((req, res) => renderPage(res, "all", "找不到這個頁面。", true, 404));
  app.use((error, req, res, next) => {
    if (res.headersSent) return next(error);
    const status = error.status === 413 ? 413 : error.status === 400 ? 400 : 500;
    renderPage(res, "all", status === 413 ? "送出的資料太大。" : "處理請求時發生錯誤。", true, status);
  });
  return app;
}

module.exports = { createApp };
