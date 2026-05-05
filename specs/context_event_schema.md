# Context Event Schema

所有進入 Life OS 的輸入，無論來源為何，統一抽象為一個 **Context Event**。

## 設計原則

1. **Raw Layer 絕對不可修改**：任何人、任何系統（包括 AI）都沒有權限更改 Raw Layer 的內容。
2. **錯誤用新增覆蓋，不用修改**：說錯了就再說一條修正，舊的那條永遠留著。
3. **Metadata Layer 可由 AI 補充或修訂**：修訂時保留版本記錄，不覆蓋前版本。

---

## 結構定義

```yaml
context_event:

  # ── Raw Layer（不可修改）──────────────────────────────
  id:
    type: string (UUID v4)
    rule: 系統自動生成，人與 AI 均不可修改
    example: "a3f8c2d1-4b5e-4f6a-9c8d-1e2f3a4b5c6d"

  timestamp:
    type: string (ISO 8601)
    timezone: Asia/Taipei (+08:00)
    rule: 以輸入當下的台北時間為準，系統自動抓取
    example: "2026-05-05T08:59:00+08:00"

  device:
    type: enum
    values:
      - apple_watch   # Apple Watch 語音輸入
      - iphone        # iPhone 任何方式輸入
      - mac           # Mac 電腦輸入
      - lark          # 飛書（含飛書機器人）
    rule: 人工選擇或由快捷指令自動帶入

  channel:
    type: enum
    values:
      - get_notes     # GET 筆記 App
      - lark_bot      # 飛書機器人對話
      - shortcut      # iOS 快捷指令
      - direct_text   # 直接打字輸入
    rule: 人工選擇或由入口自動帶入

  media_type:
    type: enum
    values:
      - voice_transcript  # 語音轉文字（轉寫結果，非原聲）
      - text              # 直接打字
      - link              # 連結（公眾號、文章等）
    rule: 由入口自動判斷帶入

  raw_content:
    type: string
    rule: 原話，一字不改。語音轉寫結果直接存入，不做任何整理。
    example: "今天跟媽媽打電話，她說她腰不太好，我有點擔心"

  # ── Metadata Layer（AI 補充，可修訂）────────────────────
  type_tag:
    type: enum
    source: 人工選（快捷指令）+ AI 同步打一份
    values: 見 type_tag_library.md

  type_tag_ai:
    type: enum
    source: AI 自動判斷，獨立於人工選擇
    purpose: 用於對比，數週後評估 AI 準確率，決定是否切換全自動

  emoji:
    type: string (single emoji)
    source: AI 從 type_tag_library.md 對照表中選取
    rule: 以 type_tag 為主依據，可參考 raw_content 細化

  ai_feedback:
    type: string
    source: AI 在寫入後自動生成
    rule: 針對這條 raw_content 給出簡短回應或反思問題，不超過 50 字
```

---

## 完整範例

```json
{
  "id": "a3f8c2d1-4b5e-4f6a-9c8d-1e2f3a4b5c6d",
  "timestamp": "2026-05-05T08:59:00+08:00",
  "device": "iphone",
  "channel": "shortcut",
  "media_type": "voice_transcript",
  "raw_content": "今天跟媽媽打電話，她說她腰不太好，我有點擔心",
  "type_tag": "family",
  "type_tag_ai": "feeling",
  "emoji": "👥",
  "ai_feedback": "你注意到擔心的感受了，有沒有想到可以做什麼讓自己安心一點？"
}
```

---

## 修正機制

當一條記錄說錯時，**不修改原始記錄**，而是新增一條修正事件：

```json
{
  "id": "new-uuid-here",
  "timestamp": "2026-05-05T09:03:00+08:00",
  "device": "iphone",
  "channel": "shortcut",
  "media_type": "text",
  "raw_content": "修正 a3f8c2d1：媽媽說的是膝蓋不好，不是腰",
  "type_tag": "daily",
  "type_tag_ai": "daily",
  "emoji": "👱‍♀️",
  "ai_feedback": ""
}
```

---

## 版本

- v0.1 — 2026-05-05 初稿，確立 Raw/Metadata 雙層結構
