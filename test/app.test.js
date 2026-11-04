"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { once } = require("node:events");
const { createApp } = require("../app");

async function withApp(t) {
  const server = createApp().listen(0, "127.0.0.1");
  await once(server, "listening");
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const base = `http://127.0.0.1:${server.address().port}`;
  return {
    get: (url = "/") => fetch(base + url),
    post: (url, data = {}) => fetch(base + url, {
      method: "POST", body: new URLSearchParams(data), redirect: "manual"
    })
  };
}

test("A3：空清單正常顯示，HTML 由伺服器直接輸出", async (t) => {
  const app = await withApp(t);
  const response = await app.get();
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /目前沒有任務/);
  assert.match(html, /id="total-count">0</);
  assert.doesNotMatch(html, /<script/);
});

test("A3：新增 trim、303 redirect，刷新 GET 不會重複新增", async (t) => {
  const app = await withApp(t);
  const response = await app.post("/tasks", { name: "  完成實作  ", filter: "pending" });
  assert.equal(response.status, 303);
  assert.match(response.headers.get("location"), /filter=pending/);
  for (let i = 0; i < 2; i++) {
    const html = await (await app.get()).text();
    assert.match(html, /<span class="task-name">完成實作<\/span>/);
    assert.match(html, /id="total-count">1</);
  }
});

test("拒絕空白、過長及重複欄位輸入", async (t) => {
  const app = await withApp(t);
  for (const name of ["", "   ", "x".repeat(201)]) {
    assert.equal((await app.post("/tasks", { name })).status, 400);
  }
  const data = new URLSearchParams([["name", "a"], ["name", "b"]]);
  assert.equal((await app.post("/tasks", data)).status, 400);
  assert.match(await (await app.get()).text(), /id="total-count">0</);
});

test("完成、重送更新與取消完成：狀態及整體統計正確", async (t) => {
  const app = await withApp(t);
  await app.post("/tasks", { name: "第一項" });
  for (let i = 0; i < 2; i++) await app.post("/tasks/1/update", { completed: "on" });
  let html = await (await app.get()).text();
  assert.match(html, /id="completed-count">1</);
  assert.match(html, /name="completed" checked/);
  await app.post("/tasks/1/update");
  html = await (await app.get()).text();
  assert.match(html, /id="completed-count">0</);
  assert.match(html, /id="pending-count">1</);
});

test("篩選只改顯示，篩選後依固定 ID 刪除指定同名任務", async (t) => {
  const app = await withApp(t);
  await app.post("/tasks", { name: "同名任務" });
  await app.post("/tasks", { name: "同名任務" });
  await app.post("/tasks/2/update", { completed: "on" });
  let html = await (await app.get("/?filter=completed")).text();
  assert.match(html, /data-task-id="2"/);
  assert.doesNotMatch(html, /data-task-id="1"/);
  assert.match(html, /id="total-count">2</);
  const deletion = await app.post("/tasks/2/delete", { filter: "completed" });
  assert.match(deletion.headers.get("location"), /filter=completed/);
  html = await (await app.get("/?filter=completed")).text();
  assert.match(html, /目前沒有符合此篩選的任務/);
  html = await (await app.get("/?filter=pending")).text();
  assert.match(html, /data-task-id="1"/);
  assert.doesNotMatch(html, /data-task-id="2"/);
  await app.post("/tasks/1/delete");
  assert.match(await (await app.get()).text(), /目前沒有任務/);
});

test("不存在及無效的 ID 不會誤刪資料；無效篩選退回全部", async (t) => {
  const app = await withApp(t);
  await app.post("/tasks", { name: "保留這項" });
  for (const id of ["999", "NaN", "0", "1abc", "-1"]) {
    for (const action of ["update", "delete"]) {
      assert.equal((await app.post(`/tasks/${id}/${action}`)).status, 404);
    }
  }
  const html = await (await app.get("/?filter=__proto__&message=__proto__")).text();
  assert.match(html, /保留這項/);
  assert.match(html, /id="total-count">1</);
});

test("HTML 名稱安全跳脫，不能插入 script 或 img", async (t) => {
  const app = await withApp(t);
  await app.post("/tasks", { name: '<img src=x onerror="alert(1)">' });
  const html = await (await app.get()).text();
  assert.doesNotMatch(html, /<img/);
  assert.match(html, /&lt;img/);
});

test("重新建立伺服器陣列會清空；未知頁面回傳 404", async (t) => {
  const first = await withApp(t);
  await first.post("/tasks", { name: "暫存資料" });
  const second = await withApp(t);
  assert.match(await (await second.get()).text(), /id="total-count">0</);
  assert.equal((await second.get("/missing")).status, 404);
});
