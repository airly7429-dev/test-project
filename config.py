import os
from dotenv import load_dotenv

load_dotenv()

FEISHU_APP_ID = os.environ["FEISHU_APP_ID"]
FEISHU_APP_SECRET = os.environ["FEISHU_APP_SECRET"]
FEISHU_DOC_ID = os.environ["FEISHU_DOC_ID"]           # 文檔 ID（URL 裡的那串）
FEISHU_BITABLE_APP_TOKEN = os.environ["FEISHU_BITABLE_APP_TOKEN"]  # 多維表格 app token
FEISHU_BITABLE_TABLE_ID = os.environ["FEISHU_BITABLE_TABLE_ID"]    # 表格 table ID
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")  # 可選：iPhone 請求鑑權
