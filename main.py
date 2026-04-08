from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

import config
import feishu_client

app = FastAPI()

CST = timezone(timedelta(hours=8))


class RecordRequest(BaseModel):
    text: str
    project: str = "未分類"
    category: str = "一般"
    secret: Optional[str] = None  # iPhone 快捷指令帶過來的鑑權碼


@app.post("/record")
def record(req: RecordRequest):
    # 簡單鑑權：如果設了 WEBHOOK_SECRET，請求必須帶上一致的 secret
    if config.WEBHOOK_SECRET and req.secret != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.now(CST)
    timestamp_str = now.strftime("%Y-%m-%d %H:%M")          # 文檔顯示用
    timestamp_ms = int(now.timestamp() * 1000)               # Bitable 日期欄位用

    token = feishu_client.get_tenant_access_token(
        config.FEISHU_APP_ID, config.FEISHU_APP_SECRET
    )

    errors = []

    # 1. 寫入飛書文檔
    try:
        feishu_client.append_to_doc(
            token, config.FEISHU_DOC_ID, req.text, timestamp_str
        )
    except Exception as e:
        errors.append(f"文檔寫入失敗: {e}")

    # 2. 寫入多維表格
    try:
        record_id = feishu_client.add_bitable_record(
            token,
            config.FEISHU_BITABLE_APP_TOKEN,
            config.FEISHU_BITABLE_TABLE_ID,
            project=req.project,
            timestamp_ms=timestamp_ms,
            content=req.text,
            category=req.category,
        )
    except Exception as e:
        errors.append(f"多維表格寫入失敗: {e}")
        record_id = None

    if errors:
        # 部分失敗時回傳 207，讓快捷指令知道有問題
        return {"status": "partial_error", "errors": errors, "record_id": record_id}

    return {"status": "ok", "record_id": record_id, "timestamp": timestamp_str}


@app.get("/health")
def health():
    return {"status": "ok"}
