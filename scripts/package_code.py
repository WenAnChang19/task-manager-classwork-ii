"""Build and verify the source-only submission ZIP (no node_modules)."""
from pathlib import Path
import zipfile
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'output/zip/B13901163_WebApp_II_Code.zip'
DEST.parent.mkdir(parents=True,exist_ok=True)
readme = '''# Web App 個人課堂實作 II
B13901163 電機三 張玟銨

需要 Node.js 20 以上。
在本資料夾執行：
  npm ci
  npm start
瀏覽器開啟 http://localhost:2234
按 Ctrl+C 停止。npm test 執行 HTTP 整合測試。

勾選 checkbox 後按「更新」儲存。資料暫存在伺服器陣列，
重新整理保留，伺服器重啟清空。程式不需要資料庫。
SQL 題為獨立作業，請在教師指定的 W3Schools 編輯器執行 sql/ 各檔。

本 ZIP 僅包含可執行程式、測試及 SQL，不含 node_modules。
報告 PDF、截圖與 AI 使用紀錄另於完整 repo 保存：
https://github.com/WenAnChang19/task-manager-classwork-ii

Task I 介面及 CSS 來源：
https://github.com/WenAnChang19/task-manager-classwork
AI 工具 Codex 協助實作與驗證，完整揭露見獨立報告。
'''
files=[ROOT/n for n in ['app.js','server.js','package.json','package-lock.json','.gitignore']]
for folder in ['public','views','test','sql']:
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for file in sorted(files):
        z.write(file,'task-manager-classwork-ii/'+file.relative_to(ROOT).as_posix())
    z.writestr('task-manager-classwork-ii/README.md',readme)
with zipfile.ZipFile(DEST) as z:
    assert z.testzip() is None
    assert not any('node_modules' in name for name in z.namelist())
    assert any(name.endswith('package-lock.json') for name in z.namelist())
    print(DEST, len(z.namelist()),'files')
