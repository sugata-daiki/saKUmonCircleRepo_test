import os
import base64
import glob
import zipfile
import requests
from notion2md.exporter.block import MarkdownExporter

# 環境変数 or 手動設定
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "sugata-daiki/saKUmonCircleRepo_test"
PATH_TO_FILE = "math/2025/sugata"
NOTION_PAGE_ID = ""
NOTION_TOKEN = ""  # 正しいトークンに置き換えてください

# 出力先
EXPORT_PATH = "./export"
os.makedirs(EXPORT_PATH, exist_ok=True)

# Notion ページを zip としてエクスポート
zip_path = MarkdownExporter(
    block_id=NOTION_PAGE_ID,
    output_path=EXPORT_PATH,
    download=False,
    token=NOTION_TOKEN
).export()

# zip 解凍
with zipfile.ZipFile("./export/" + NOTION_PAGE_ID +  ".zip", "r") as zip_ref:
    zip_ref.extractall(EXPORT_PATH)

# 解凍された .md ファイルのうち最初のものを選ぶ（通常1ファイル）
md_files = glob.glob(os.path.join(EXPORT_PATH, "**/*.md"), recursive=True)
if not md_files:
    raise FileNotFoundError("解凍されたフォルダに .md ファイルが見つかりませんでした")

latest_md_path = md_files[0]
filename = os.path.basename(latest_md_path)

# base64エンコードしてGitHubにアップロード
with open(latest_md_path, "rb") as f:
    content = base64.b64encode(f.read()).decode()

url = f"https://api.github.com/repos/{REPO}/contents/{PATH_TO_FILE}/{filename}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
data = {
    "message": "Upload Notion page as Markdown",
    "content": content
}

res = requests.put(url, headers=headers, json=data)
print(f"GitHub upload status: {res.status_code}")
print(res.json())
