import time
import httpx

BASE_URL = "https://open.feishu.cn/open-apis"

# Token 快取，避免每次請求都重新取
_token_cache: dict = {"token": None, "expires_at": 0}


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]

    resp = httpx.post(
        f"{BASE_URL}/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"飛書 token 取得失敗: {data}")

    _token_cache["token"] = data["tenant_access_token"]
    _token_cache["expires_at"] = now + data["expire"] - 60  # 提前 60 秒刷新
    return _token_cache["token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ── 飛書文檔 ──────────────────────────────────────────────────────────────────

def get_doc_root_block(token: str, doc_id: str) -> str:
    """取得文檔根 block ID（用來追加內容到文末）"""
    resp = httpx.get(
        f"{BASE_URL}/docx/v1/documents/{doc_id}",
        headers=_headers(token),
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"取得文檔失敗: {data}")
    return data["data"]["document"]["body"]["block_id"]


def append_to_doc(token: str, doc_id: str, text: str, timestamp: str) -> None:
    """在文檔末尾追加一個段落（含時間戳）"""
    root_block_id = get_doc_root_block(token, doc_id)

    # block_type：1 = paragraph, 2 = heading1, 3 = heading2
    blocks = [
        {
            "block_type": 3,  # heading2
            "heading2": {
                "elements": [{"text_run": {"content": timestamp}}]
            },
        },
        {
            "block_type": 1,  # paragraph
            "paragraph": {
                "elements": [{"text_run": {"content": text}}]
            },
        },
    ]

    resp = httpx.post(
        f"{BASE_URL}/docx/v1/documents/{doc_id}/blocks/{root_block_id}/children",
        headers=_headers(token),
        json={"children": blocks, "index": -1},  # index=-1 追加到末尾
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"寫入文檔失敗: {data}")


# ── 飛書多維表格 ──────────────────────────────────────────────────────────────

def add_bitable_record(
    token: str,
    app_token: str,
    table_id: str,
    project: str,
    timestamp_ms: int,
    content: str,
    category: str,
) -> str:
    """在多維表格新增一筆記錄，回傳 record_id"""
    resp = httpx.post(
        f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records",
        headers=_headers(token),
        json={
            "fields": {
                "項目": project,
                "時間": timestamp_ms,   # 飛書日期欄位用毫秒時間戳
                "內容": content,
                "分類": category,
            }
        },
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"寫入多維表格失敗: {data}")
    return data["data"]["record"]["record_id"]
