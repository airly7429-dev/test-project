# OpenClaw Command Set

OpenClaw 作為 Life OS 的 Bridge Agent，負責：
1. 接收來自快捷指令（Layer 3）的輸入
2. 將資料寫入飛書 Bitable（Layer 1）
3. 執行 AI 打標，填入 Metadata Layer

---

## 指令總覽

| 指令 | 用途 |
|---|---|
| `/log` | 新增一筆 Context Event（主要入口） |
| `/correct` | 對已存在的記錄新增一筆修正事件 |
| `/today` | 查詢今日所有 Context Events |

---

## `/log` — 新增 Context Event

### 功能
接收原始輸入，自動組裝 Context Event，寫入飛書 Bitable，並執行 AI 打標。

### 輸入參數

| 參數 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `raw_content` | string | ✅ | 原始輸入內容，一字不改 |
| `device` | enum | ✅ | `apple_watch` / `iphone` / `mac` / `lark` |
| `channel` | enum | ✅ | `get_notes` / `lark_bot` / `shortcut` / `direct_text` |
| `media_type` | enum | ✅ | `voice_transcript` / `text` / `link` |
| `type_tag` | enum | ❌ | 人工選擇的類型標籤（見 type_tag_library.md）；未提供時欄位留空 |

### 處理流程

```
1. 生成 UUID v4 → id
2. 抓取當前台北時間（+08:00）→ timestamp
3. 將 Raw Layer 寫入飛書 Bitable
4. AI 執行打標：
   a. 根據 raw_content 判斷 type_tag_ai（依 type_tag_library.md 規則）
   b. 根據 type_tag（若有）或 type_tag_ai 選取 emoji
   c. 生成 ai_feedback（≤50 字）
5. 將 Metadata Layer 更新至同一筆記錄
6. 回傳確認訊息
```

### 回傳格式

```
✅ 已記錄
[emoji] [ai_feedback]
```

### 範例

**輸入：**
```
/log
raw_content: "今天跟媽媽打電話，她說她腰不太好，我有點擔心"
device: iphone
channel: shortcut
media_type: voice_transcript
type_tag: family
```

**回傳：**
```
✅ 已記錄
👥 你注意到擔心的感受了，有沒有想到可以做什麼讓自己安心一點？
```

---

## `/correct` — 新增修正事件

### 功能
對某筆錯誤記錄新增一筆修正事件。遵守 Raw Layer 不可修改原則，修正以新增方式覆蓋。

### 輸入參數

| 參數 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `original_id` | string (UUID) | ✅ | 被修正的原始記錄 id |
| `correction` | string | ✅ | 修正內容說明 |
| `device` | enum | ✅ | 同 `/log` |
| `channel` | enum | ✅ | 同 `/log` |
| `media_type` | enum | ✅ | 同 `/log` |

### 處理流程

```
1. 生成新 UUID v4 → id
2. 抓取當前台北時間 → timestamp
3. 自動組裝 raw_content = "修正 {original_id}：{correction}"
4. type_tag = daily（固定）、type_tag_ai = daily（固定）
5. emoji = 👱‍♀️（daily 固定 emoji）
6. ai_feedback = ""（留空）
7. 寫入飛書 Bitable
8. 回傳確認訊息
```

### 回傳格式

```
✅ 修正已記錄（原始 ID：{original_id}）
```

### 範例

**輸入：**
```
/correct
original_id: "a3f8c2d1-4b5e-4f6a-9c8d-1e2f3a4b5c6d"
correction: "媽媽說的是膝蓋不好，不是腰"
device: iphone
channel: shortcut
media_type: text
```

**回傳：**
```
✅ 修正已記錄（原始 ID：a3f8c2d1-4b5e-4f6a-9c8d-1e2f3a4b5c6d）
```

---

## `/today` — 查詢今日 Context Events

### 功能
查詢今日（台北時間 00:00 至當下）所有已記錄的 Context Events，依時間倒序排列。

### 輸入參數

無（自動以今日台北日期為範圍）

### 回傳格式

```
📋 今日記錄（{N} 筆）

{timestamp_short} [{emoji}] {raw_content_preview}
...
```

- `timestamp_short`：僅顯示 HH:MM
- `raw_content_preview`：原始內容前 30 字，超過截斷加 `…`

### 範例

**回傳：**
```
📋 今日記錄（3 筆）

09:12 [👥] 今天跟媽媽打電話，她說她腰不太好，我有點擔心
08:45 [💼] 客戶說這個月想暫停合作，需要跟進
08:30 [✅] 讀完《原子習慣》第三章，發現「身份認同先於行為…
```

---

## AI 打標規則（`/log` 專用）

OpenClaw 在打標時遵守以下規則，詳細說明見 `type_tag_library.md`：

1. 以 `raw_content` 的**主要意圖**判斷 `type_tag_ai`，不以關鍵詞硬匹配
2. 若有人工 `type_tag`，以 `type_tag` 為主選取 `emoji`；若無則以 `type_tag_ai`
3. 若無法判斷類型，`type_tag_ai` 預設為 `daily`
4. `type_tag` 與 `type_tag_ai` 分開儲存，**互不覆蓋**
5. `ai_feedback` 不超過 50 字，以問句或簡短回應為主

---

## 版本紀錄

| 版本 | 日期 | 變更 |
|---|---|---|
| v0.1 | 2026-05-05 | 初稿，定義 `/log`、`/correct`、`/today` 三個核心指令 |
