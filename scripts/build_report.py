"""Rebuild the Markdown report and PDF from actual source and evidence files.

Dependencies: reportlab, Pillow. Optional render/QA: PyMuPDF, pypdf.
Run with a Python environment that provides these packages.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
import json
import re
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, Table, TableStyle, Image, PageBreak, NextPageTemplate, Preformatted)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/B13901163_WebApp_II_Report.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
regular = Path('/System/Library/Fonts/STHeiti Light.ttc')
bold = Path('/System/Library/Fonts/STHeiti Medium.ttc')
if not regular.exists():
    raise SystemExit('Provide a Traditional Chinese TrueType font and update the font paths.')
pdfmetrics.registerFont(TTFont('CJK', str(regular), subfontIndex=0))
pdfmetrics.registerFont(TTFont('CJKB', str(bold), subfontIndex=0))
pdfmetrics.registerFontFamily('CJK', normal='CJK', bold='CJKB')

styles = {
 'title': ParagraphStyle('title', fontName='CJKB', fontSize=21, leading=29, textColor=colors.HexColor('#162c46'), spaceAfter=15, wordWrap='CJK'),
 'landscapeTitle': ParagraphStyle('landscapeTitle', fontName='CJKB', fontSize=16, leading=21, textColor=colors.HexColor('#162c46'), spaceAfter=6, wordWrap='CJK'),
 'h2': ParagraphStyle('h2', fontName='CJKB', fontSize=13, leading=19, spaceBefore=11, spaceAfter=6, textColor=colors.HexColor('#1d4ed8'), wordWrap='CJK'),
 'body': ParagraphStyle('body', fontName='CJK', fontSize=10.5, leading=17, spaceAfter=8, wordWrap='CJK'),
 'small': ParagraphStyle('small', fontName='CJK', fontSize=8.5, leading=13, spaceAfter=6, wordWrap='CJK'),
 'cell': ParagraphStyle('cell', fontName='CJK', fontSize=9, leading=14, wordWrap='CJK'),
 'head': ParagraphStyle('head', fontName='CJKB', fontSize=9, leading=14, textColor=colors.white, wordWrap='CJK'),
 'code': ParagraphStyle('code', fontName='Courier', fontSize=8.2, leading=12, backColor=colors.HexColor('#f1f5f9'), borderPadding=9, spaceBefore=6, spaceAfter=12),
}
story, md = [], []
current = 'portrait'
started = False

def page(title, orientation='portrait'):
    global current, started
    if started:
        story.extend([NextPageTemplate(orientation), PageBreak()])
        md.append('\n<!-- page: ' + orientation + ' -->\n')
    current = orientation
    started = True
    story.append(Paragraph(escape(title), styles['landscapeTitle' if orientation == 'landscape' else 'title']))
    md.append('# ' + title + '\n')

def p(text, small=False):
    story.append(Paragraph(escape(text).replace('\n', '<br/>'), styles['small' if small else 'body']))
    md.append(text + '\n')

def h(text):
    story.append(Paragraph(escape(text), styles['h2']))
    md.append('## ' + text + '\n')

def code(text, language='javascript'):
    # Source snippets are ASCII; explanatory Chinese is placed in normal paragraphs.
    story.append(Preformatted(text.rstrip(), styles['code']))
    md.extend(['```' + language, text.rstrip(), '```\n'])

def table(rows, widths=None):
    width = 505 if current == 'portrait' else 752
    if widths is None: widths = [width / len(rows[0])] * len(rows[0])
    data = [[Paragraph(escape(str(v)), styles['head' if i == 0 else 'cell']) for v in row] for i,row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
      ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#234b75')),
      ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f5f9')]),
      ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d7dee8')),
      ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),
      ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),
      ('BOTTOMPADDING',(0,0),(-1,-1),7)
    ]))
    story.extend([t,Spacer(1,8)])
    md.append('| ' + ' | '.join(map(str,rows[0])) + ' |')
    md.append('| ' + ' | '.join(['---']*len(rows[0])) + ' |')
    for row in rows[1:]: md.append('| ' + ' | '.join(map(str,row)) + ' |')
    md.append('')

def shot(file, caption):
    source = ROOT / 'evidence' / file
    w,h = PILImage.open(source).size
    scale = min(736/w, 442/h)
    story.append(Image(str(source),width=w*scale,height=h*scale,hAlign='CENTER'))
    story.append(Spacer(1,5))
    story.append(Paragraph(escape(caption), styles['small']))
    md.append(f'![{caption}](evidence/{file})\n')

browser = json.loads((ROOT/'evidence/browser-tests.json').read_text())
sql = json.loads((ROOT/'evidence/sql-results.json').read_text())
verified = json.loads((ROOT/'evidence/sql-verification.json').read_text())
time_text = datetime.fromisoformat(verified['verifiedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')

page('Web App 個人課堂實作 II')
p('B13901163　電機三　張玟銨\n實作日期：2026-11-04　｜　Node.js / Express / EJS / SQL')
h('A1. 任務管理器與執行方式')
p('延續課堂實作 I 的灰白與藍色介面，將資料及操作搬到伺服器。使用 Express 建立網站，EJS 顯示新增、查看、完成／取消完成、刪除及三種篩選。完成狀態必須勾選後按「更新」才會儲存。')
code('npm ci\nnpm start\n# Open http://localhost:2234', 'bash')
p('實測環境：Node.js 26.3.0、Express 5.3.0、EJS 3.1.10。server.js 固定監聽本機 2234。資料存在 tasks 陣列，重新整理保留，伺服器重啟清空；不同瀏覽器共用同一份陣列。')
h('A2. GET 與 POST 的用途')
table([
 ['HTTP','路徑','用途'],
 ['GET','/ 或 /?filter=...','取得完整頁面；all / pending / completed 篩選'],
 ['POST','/tasks','解析任務名稱，驗證後新增'],
 ['POST','/tasks/:id/update','依固定 ID 設定 completed'],
 ['POST','/tasks/:id/delete','依固定 ID 刪除指定任務']
], [50,150,305])
h('為什麼屬於伺服器端產生頁面？')
p('GET 路由把陣列與篩選結果傳給 res.render("index", ...)。EJS 的迴圈在 Node.js 端產生清單 HTML，瀏覽器收到的回應已包含任務內容，不需要執行 renderTasks() 才能看見任務。網站沒有前端 JavaScript，表單仍可操作。')
p('POST 成功後以 303 重新導向 GET（Post/Redirect/Get）。因此刷新頁面只會再次讀取清單，不會重複新增。篩選值放在表單 hidden input，讓修改後回到原篩選。',small=True)

page('A2. 表單資料、陣列與頁面')
h('接收表單資料：app.js 第 17 行與第 52-58 行')
code('app.use(express.urlencoded({ extended: false, limit: "10kb" }));\n\napp.post("/tasks", (req, res) => {\n  const filter = getFilter(req.body.filter);\n  const name = typeof req.body.name === "string"\n    ? req.body.name.trim() : "";\n  if (!name) return renderPage(res, filter,\n    "Please enter a task.", true, 400);\n  tasks.push({ id: nextTaskId++, name, completed: false });\n  redirectToList(res, filter, "added");\n});')
p('上方為縮短的流程示意；實際程式的訊息為中文，並有 200 字元長度限制。express.urlencoded 將表單轉為 req.body。trim() 去除前後空白，空白輸入回傳 400 並重新顯示頁面。')
h('修改陣列：app.js 第 66 行與第 74 行')
code('task.completed = req.body.completed === "on";\n\ntasks.splice(tasks.findIndex((item) => item.id === task.id), 1);')
p('checkbox 未勾選時不會傳送 completed，故以 === "on" 判斷。明確設定狀態使相同更新重送後仍一致。刪除使用固定 ID，不使用篩選後的顯示索引，所以同名任務或篩選後操作也不會誤刪。')
h('重新顯示頁面：app.js 第 24-37 行')
code('res.status(status).render("index", {\n  tasks: visibleTasks, filter, filterLabels, message, isError, input,\n  total: tasks.length, completedCount,\n  pendingCount: tasks.length - completedCount\n});\n\nres.redirect(303, `/?${new URLSearchParams({ filter, message })}`);')
p('統計從完整陣列計算，篩選只決定 visibleTasks。EJS 以跳脫輸出的 <%= task.name %> 顯示名稱，避免輸入被當成 HTML。找不到 ID 時回傳 404，保留其他任務。',small=True)

for title,file,caption in [
 ('A1 證據 1/5：新增任務','A1-add.jpg','新增「完成 Web App 實作」後，出現成功提示；統計為總數 1、未完成 1、已完成 0。'),
 ('A1 證據 2/5：查看任務','A1-view.jpg','三項任務完整顯示，每項均有 checkbox、更新與刪除按鈕；統計 3/3/0。'),
 ('A1 證據 3/5：完成任務','A1-complete.jpg','勾選 JavaScript 練習並按更新後，顯示勾選與刪除線，統計 3/2/1。'),
 ('A1 證據 4/5：篩選任務','A1-filter.jpg','已完成篩選只顯示 JavaScript 練習；整體統計維持 3/2/1。'),
 ('A1 證據 5/5：刪除指定任務','A1-delete.jpg','在已完成篩選刪除 JavaScript 練習，再查看全部；另外兩項仍保留，統計 2/2/0。')
]:
    page(title,'landscape');shot(file,caption)

page('A3. 測試與基本可靠性')
p('執行者：Codex 自動操作本機 HTTP 與 in-app Chromium。以下為本次實際紀錄，不沿用 Task I 的結果。HTTP 整合測試使用 Node 內建 node:test，以獨立 app 啟動隔離伺服器，執行 npm test。')
table([
 ['測試','實際結果','判定'],
 ['空清單','HTTP 200；顯示提示與 0/0/0；HTML 已有頁面內容','PASS'],
 ['新增與刷新','名稱 trim；303 導向 GET；重複 GET 不會新增第二筆','PASS'],
 ['空白、過長、重複欄位','回傳 400，不新增任務','PASS'],
 ['完成、重送、取消完成','重送相同狀態不反轉；取消後統計恢復','PASS'],
 ['篩選後刪除同名任務','只移除指定 ID；保留其他任務；最後可回空清單','PASS'],
 ['錯誤 ID 與篩選','不存在或無效 ID 回 404；其他資料不受影響','PASS'],
 ['HTML 輸入跳脫','輸入 img 字串不會產生圖片元素','PASS'],
 ['伺服器重建及未知頁面','新 app 陣列為空；未知路徑回 404','PASS']
],[131,324,50])
p('HTTP 結果：8/8 通過，0 失敗。原始輸出：evidence/node-test-output.txt。瀏覽器另完成 11 項操作紀錄，包含新增、指定刪除、空清單、純空白驗證、完成與取消、三種篩選、刷新與長名稱。',small=True)
h('可靠性與驗證範圍')
p('CSS 保留 Task I 的 480px 響應式規則。本次桌面 viewport 實測為 1280px，長名稱可換行且沒有水平溢出。手機尺寸覆寫沒有改變實際 viewport，因此手機 runtime gate 記為 not_performed，不宣稱已完成手機實測。')
p('本作業以單人、本機示範為範圍，沒有資料持久化、帳號或多人隔離。A 題依規定不連接 SQL 資料庫。',small=True)

page('A3 證據：無任務仍正常顯示','landscape')
shot('A3-empty.jpg','啟動後 tasks 為空，清單顯示「目前沒有任務」，表單及篩選可操作，統計 0/0/0。HTTP 測試亦驗證刪除最後一項後正常回到空清單。')

sql_titles = ['B1. 法國顧客消費總額','B2. 1996 年 7 月銷售量前五名','B3. 購買 Tofu 的顧客與訂單']
sql_files = ['B1_france_total.sql','B2_july_top5.sql','B3_tofu_orders.sql']
sql_shots = ['B1-france.jpg','B2-july-top5.jpg','B3-tofu.jpg']
explanations = [
 '使用 Customers → Orders → OrderDetails → Products 四張表，依 CustomerID、OrderID、ProductID 連接。WHERE 限定 France，SUM(Price × Quantity) 計算金額，依顧客分組，TotalSpent 遞減排序。本查詢列出有訂單明細的法國顧客；INNER JOIN 不產生無交易顧客的零元列。',
 '使用 Products、OrderDetails、Orders 三張表。日期採左閉右開區間，包含 7 月 1 日至 7 月 31 日，也適用於日期含時間的欄位。依產品分組加總 Quantity，排序後 TOP 5。數量同分時以 ProductID 遞增決定穩定順序。',
 '使用 Customers、Orders、OrderDetails、Products 四張表，限定 ProductName = Tofu。每一列保留一筆購買明細，不使用 GROUP BY 或 DISTINCT，避免把同一顧客不同日期的訂單合併。CustomerID 遞增，同顧客再依日期及訂單編號排序。'
]
for i,result in enumerate(sql):
    page(sql_titles[i])
    p('執行環境：教師指定 W3Schools SQLSERVER Tryit Editor。三題均實際按 Run SQL，使用網站回傳結果；SQL 指令如下。',small=True)
    code((ROOT/'sql'/sql_files[i]).read_text(),'sql')
    p(explanations[i])
    h('實際執行結果')
    widths = [85,320,100] if i<2 else [85,240,110,70]
    table(result['rows'],widths)
    p(f'回傳 {len(result["rows"])-1} 筆。完整查詢與結果截圖見下一頁；可複製的 SQL 另存於 sql/{sql_files[i]}。',small=True)
    page(sql_titles[i]+'：網站執行證據','landscape')
    caption = (f'教師指定網址的真實執行畫面，包含 Run SQL、結果表頭、全部 {len(result["rows"])-1} 筆結果及資料表列表。編輯器有獨立捲動，完整 SQL 已於前頁以文字列出。' if i<2 else '教師指定網址的真實執行畫面，顯示回傳 8 筆與前段結果。結果區有獨立捲動，下頁補後段畫面；完整 8 筆已在文字表列出。')
    shot(sql_shots[i],caption)
    if i==2:
        page('B3. Tofu 訂單：結果區後段','landscape')
        shot('B3-tofu-bottom.jpg','捲動結果區後顯示後段明細，包含 CustomerID 81 及 87 的兩筆訂單；與前頁同一次查詢，未修改資料或 SQL。')

page('B. 結果交叉驗證與資料範圍')
p('指定環境：https://www.w3schools.com/sql/trysqlserver.asp?filename=trysql_func_sqlserver_cast',small=True)
h('不只確認 SQL 能執行')
p('另外在同一編輯器執行 verification-detail.sql，取得尚未 GROUP BY 的顧客、國家、訂單、日期、產品、單價及數量。網站實際回傳 518 筆連接明細，由 JavaScript 獨立篩選、彙總、排序，逐列比對 B1、B2、B3。')
table([
 ['查詢','獨立重算與檢查','結果'],
 ['B1','篩選 France，以整數分計算每列單價乘數量，再依顧客加總及排序；7 筆完全一致。','PASS'],
 ['B2','篩選完整 1996 年 7 月，依 ProductID 加總數量及取前五；105、100、95、85、77 完全一致。','PASS'],
 ['B3','篩選 ProductName 為 Tofu，保留每筆明細及日期；8 筆欄位與排序完全一致。','PASS']
],[48,407,50])
p('交叉驗證時間（Asia/Taipei）：'+time_text+'。驗證查詢及原始結果保留於 sql/verification-detail.sql、evidence/sql-detail.json、evidence/sql-results.json、evidence/sql-verification.json。',small=True)
h('資料範圍與解讀')
p('八張表中，這三題只需要 Customers、Orders、OrderDetails、Products；Categories、Employees、Shippers、Suppliers 不影響要求的欄位。額外連接無關表格沒有必要，也可能增加錯誤或重複計算風險。')
p('消費金額完全依題目指定的 Products.Price × OrderDetails.Quantity 計算，沒有另外引入折扣或歷史價格。網站側欄的靜態表筆數與本次查詢實際回傳資料範圍不同；本報告採實際查詢回傳值，沒有從其他 Northwind 資料版本拼補結果。')
h('來源')
p('Task I：https://github.com/WenAnChang19/task-manager-classwork\n本次 repo：https://github.com/WenAnChang19/task-manager-classwork-ii\nExpress：https://expressjs.com/en/5x/api/\nEJS：https://ejs.co/\nNode 測試器：https://nodejs.org/api/test.html',small=True)

page('C1. AI 對話紀錄：後端表單')
p('使用工具：OpenAI Codex。以下保留本聊天真實問答節錄，處理與驗證均標明執行者，沒有把事後整理的問題冒充學生原話。')
h('遇到的問題')
p('將 Task I 的瀏覽器端陣列及手動 DOM 更新改成 Express/EJS，並確定完成任務的表單提交方式。')
h('學生提問與決定（實際節錄）')
p('「這是task1的repo 先跟我確認所有你覺得需要釐清的技術細節」\n確認操作方式時回覆：「保留 採勾選後按更新」。')
h('AI 回覆（實際節錄）')
p('「這次要把任務資料與處理邏輯搬到 Express，透過 EJS 產生頁面。」\n「完成狀態採『勾選後按更新』的表單方式，讓每次操作都能清楚對應後端 POST」。')
h('採用與處理方式')
p('學生選擇沿用介面並採勾選後按更新。Codex 依此實作伺服器 tasks、POST 更新、303 導向 GET 及 EJS。更新以 req.body.completed === "on" 明確指定狀態，不直接把布林值反轉，避免重送導致再次切換。')
h('驗證結果')
p('Codex 瀏覽器操作確認：只勾選時已完成數仍為 0，按更新才變成 1；取消勾選後按更新可恢復。HTTP 測試另驗證相同更新重送仍維持已完成。證據為 A1-complete.jpg、browser-tests.json 的 UI04/UI10，以及 node-test-output.txt。')
p('更完整的合作節錄與來源說明見 docs/AI_COLLABORATION.md。',small=True)

page('C1. AI 對話紀錄：SQL 驗證')
h('遇到的問題')
p('必須從八張表選出正確關聯，並在教師指定環境實際執行，不能只提交看似正確的 AI 指令。')
h('學生提供的要求（實際訊息節錄）')
p('「SQL 指令必須實際執行，不能只提交看起來合理的指令。」\n「請注意：必須正確地從八個資料表選出適當的資料表、連接與篩選。」')
p('上述文字是學生貼上的教師要求，並非另行提出的除錯問題。',small=True)
h('AI 回覆（實際節錄）')
p('「先確認實際環境支援的語法，再決定前五筆及日期條件寫法。」\n執行後回報：「三題 SQL 已在指定網站執行成功：B1 回傳 7 筆、B2 回傳 5 筆、B3 回傳 8 筆。」')
h('採用與處理方式')
p('Codex 在指定網站執行三題，B2 使用該環境可執行的 TOP 5 與完整月份區間。為避免查詢能跑但連接或彙總錯誤，另查出未彙總明細，以 JavaScript 重算三題並比對。沒有把這些操作寫成學生親自執行。')
h('驗證結果')
p('518 筆明細重算後，三題欄位、排序及數值一致。B1 使用整數分避開 JavaScript 浮點誤差。截圖、原始明細及比對紀錄均保存在 evidence/。')

page('C2. 學習反思')
p('以下由 AI 依本次實際開發與驗證過程協助撰寫，參考 Task I 的精簡風格。這是供學生閱讀、核對的草稿；個人理解與感受尚未由學生確認。')
h('1. 本次實作最困難的部分及解決方式')
p('本次最需要注意的是資料與畫面更新的位置。Task I 在瀏覽器修改陣列後呼叫 renderTasks()，這次則需要由表單把資料送到 Express，再由 EJS 產生新的 HTML。可以沿著「表單欄位 → req.body → 修改 tasks → 303 → GET → res.render」逐步追蹤，確認每一個功能在哪裡發生。SQL 則先畫出顧客、訂單、明細、產品的關聯，再決定分組及篩選條件，避免把同一張訂單的金額重複計算。')
h('2. AI 建議是否需要調整？')
p('AI 的建議需要配合這次題目及操作選擇調整。例如不能直接保留 Task I 勾選後只更新瀏覽器陣列的方式；這次選擇「勾選後按更新」，所以完成狀態必須由 POST 傳到後端。未勾選的 checkbox 不會送出 completed 欄位，因此需要明確判斷是否等於 "on"。SQL 也不能只看編輯器名稱就假設所有語法可用，而要以指定網站實際執行結果為準。')
h('3. 如何確認程式與 SQL 正確？')
p('程式驗證同時採用 HTTP 測試及真實瀏覽器操作，除了正常新增、刪除與空清單，也確認篩選後刪除指定 ID、取消完成、刷新不重複新增及 HTML 跳脫。SQL 除了查看執行截圖，還使用同一環境的未彙總明細重算，逐筆比對三題結果。這些測試由 Codex 執行；提交前仍應自行操作網站並能說明各路由及 SQL 的連接與分組用途。')
h('AI 協助範圍與繳交說明')
p('Codex 協助程式生成、除錯、測試、SQL 執行、截圖、報告與 repo 整理。學生提供題目、原 repo、介面及提交方式選擇。依規範繳交本 PDF 與獨立程式 ZIP；ZIP 不包含 node_modules，使用 npm ci 安裝依賴。規範沒有要求公開部署，網站於 localhost:2234 執行。',small=True)

def decorate(canvas, doc):
    w,h = doc.pageTemplate.pagesize
    canvas.setPageSize((w,h))
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#cbd5e1'))
    canvas.line(45, h-31, w-45, h-31)
    canvas.setFont('CJK',8)
    canvas.setFillColor(colors.HexColor('#64748b'))
    canvas.drawString(45,h-23,'WEB APP II  |  B13901163  |  張玟銨')
    canvas.drawString(45,23,'2026-11-04　實際程式與 SQL 證據 / AI 協作已揭露')
    canvas.drawRightString(w-45,23,str(doc.page))
    canvas.restoreState()

doc = BaseDocTemplate(str(OUT),pagesize=A4,title='Web App 個人課堂實作 II',author='張玟銨 / Codex assisted',leftMargin=45,rightMargin=45,topMargin=48,bottomMargin=42)
for name,size in [('portrait',A4),('landscape',landscape(A4))]:
    w,h=size
    frame=Frame(45,42,w-90,h-90,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id=name)
    doc.addPageTemplates(PageTemplate(id=name,frames=[frame],onPage=decorate,pagesize=size))
(ROOT/'REPORT.md').write_text('\n'.join(md),encoding='utf8')
doc.build(story)
print(OUT)
