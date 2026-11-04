# Web App 個人課堂實作 II

使用 Node.js、Express、EJS 實作伺服器端任務管理器；SQL 題在指定 W3Schools 編輯器實際執行。介面與固定 ID 設計延續 [Task I](https://github.com/WenAnChang19/task-manager-classwork)。

## 啟動

需要 Node.js 20 以上及 npm。實測 Node.js 26.3.0、Express 5.3.0、EJS 3.1.10；精確套件版本保存在 package-lock.json。

```bash
npm ci
npm start
```

瀏覽器開啟 http://localhost:2234 。伺服器只監聽本機介面，port 固定 2234。

## 功能

- 新增、查看、完成／取消完成、刪除、全部／未完成／已完成篩選。
- 勾選 checkbox 後按「更新」才會儲存；更新及刪除後保留篩選。
- 統計以全部任務計算；篩選只影響顯示。
- 資料存於伺服器陣列，刷新頁面保留，重新啟動伺服器清空。所有瀏覽器共用同一陣列。
- 拒絕空白及超長輸入，以固定 ID 處理同名任務，EJS 跳脫使用者文字。
- 不需要資料庫、帳號或前端框架。SQL B 題獨立作答。

## 繳交

| 項目 | 檔案 |
| --- | --- |
| 實作報告 PDF | [B13901163_WebApp_II_Report.pdf](output/pdf/B13901163_WebApp_II_Report.pdf) |
| 程式 ZIP（不含 node_modules） | [B13901163_WebApp_II_Code.zip](output/zip/B13901163_WebApp_II_Code.zip) |
| 報告文字原稿 | [REPORT.md](REPORT.md) |
| SQL | [B1](sql/B1_france_total.sql)、[B2](sql/B2_july_top5.sql)、[B3](sql/B3_tofu_orders.sql) |
| 實際 AI 合作節錄 | [docs/AI_COLLABORATION.md](docs/AI_COLLABORATION.md) |
| 執行與交叉驗證資料 | [evidence/](evidence/) |


## 測試

```bash
npm test
```

8 項真實 HTTP 整合測試通過；瀏覽器操作另有 11 項紀錄與截圖。

SQL 請逐題貼入 [教師指定編輯器](https://www.w3schools.com/sql/trysqlserver.asp?filename=trysql_func_sqlserver_cast) 後按 Run SQL。B1/B2/B3 分別得到 7/5/8 筆；使用該站 518 筆交易明細重新計算，三題完全一致。網站側欄列出的資料筆數與實際回傳明細不一定一致，以本次實際查詢結果為準。

## 檔案與資料流

```text
server.js             固定 port 2234 的啟動入口
app.js                路由、表單解析、伺服器陣列及頁面呈現
views/index.ejs       由後端資料產生 HTML
public/styles.css     沿用 Task I 的樣式及響應式規則
test/app.test.js      Node 內建測試器與 HTTP 整合測試
sql/                  三題 SQL 與未彙總交叉驗證查詢
evidence/             真實截圖、結果、測試及驗證紀錄
reference/task1/      下載的 Task I 原始檔，保留來源內容
scripts/              PDF 與 ZIP 產生、驗證工具
```

瀏覽器表單 POST → express.urlencoded 解析 req.body → 修改 tasks → 303 導回 GET → EJS 產生 HTML。篩選則直接 GET /?filter=...。
