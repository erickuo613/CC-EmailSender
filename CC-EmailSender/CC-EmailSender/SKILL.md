---
name: CC-EmailSender
description: "通用郵件發送器 — 支援 Gmail、Outlook、網易(163/126/yeah/企業/靈犀)、QQ、iCloud、Yahoo 等所有電子郵件系統。每次使用時現場詢問郵箱地址與 SMTP 認證，不依賴固定設定檔，適合多人共用。觸發條件：使用者意圖涉及透過電子郵件發送或傳遞內容時。範例：發郵件、通知某人、分享檔案/報告、發送會議紀要、轉發內容、回覆摘要等。支援：收件人/抄送/暗送、AI 自動生成內文、附件、發送前預覽確認。"
agent_created: true
---

# 通用郵件發送器 (Universal Email Sender)

汎用 SMTP 郵件發送工具。不依賴任何設定檔，所有參數在每次使用時現場取得。
支援所有電子郵件提供商（Gmail、Outlook、Office365、網易、QQ、iCloud、Yahoo 等）。

## 前置需求

- Python 3.x + 標準庫（無外部依賴）
- 腳本路徑: `~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py`

---

## 觸發政策

**不要等待明確的關鍵詞。** 只要使用者的意圖涉及透過電子郵件發送內容就應觸發。

| 使用者說的話（範例） | 判讀 |
|---|---|
| "把這個報告發給王總" | 透過郵件發送報告 |
| "通知團隊明天開會" | 發郵件通知團隊 |
| "把這份記錄郵件給 zhangsan@example.com" | 發送記錄 |
| "幫我回覆那封郵件，說收到" | 撰寫並發送回覆郵件 |
| "把這個檔案分享給小張" | 透過郵件發送檔案 |
| "給客戶發一下報價單" | 發送報價單 |

若意圖不明確（可能是郵件也可能是即時訊息），**先詢問**使用者偏好哪種管道。

---

## 完整流程（6 步）

> ## ⚠️ 絕對禁令：禁止輸出任何「卡片 / 輸入框 / 表單」Artifact，禁止調用 `show_widget` / `read_me` / `present_files`
>
> 之前的版本把輸入表格渲染成 WorkBuddy 的 Artifact 卡片（或包在 code block 裡看起來像卡片），
> 顯示在 chat 中但**無法輸入**，導致流程卡死。
>
> **正確做法：直接在對話回覆文字中輸出純文字表格。** 不要調用 widget 工具、不要包 code block、不要生成 HTML/SVG。
> 卡片只是視覺引導，真正的輸入位置是對話框（使用者在下方打字 → 我從對話框讀取）。
>
> 範例格式：
> ```
> 📧 寄件人設定
> ─────────────────
> 寄件人郵箱：__________________
> ─────────────────
> 請直接在下方對話框輸入您的郵箱地址。
> ```
> 以上範例是文字，不是程式碼。實際輸出時**不要包在 ``` 裡面**。直接寫在回覆中。

---

### 第 1 步：寄件人設定（郵箱 → 偵測 → 密碼）

**非循序問答。直接在對話回覆中輸出純文字表格，使用者在下方對話框填寫。對話不停頓。**

#### 1a. 要求郵箱地址

**直接在回覆文字中輸出純文字表格（不要包在 ``` 裡，不要調用任何工具）：**

範例：

📧 寄件人設定
─────────────────
寄件人郵箱：__________________
─────────────────

請直接在下方對話框輸入您的郵箱地址。

使用者回覆郵箱後，執行自動偵測：

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --detect-smtp "使用者郵箱"
```

回傳 JSON 含 `provider_name`、`smtp_server`、`smtp_port`、`ssl_mode`、`auth_type`。

**報告結果（普通文字）：**
- 已知 → "已識別為 **[provider_name]**，伺服器 `[server]:[port]`。"
- 未知 → 用 `AskUserQuestion` 按鍵讓使用者選擇加密方式（SSL/STARTTLS/不加密），並請提供 SMTP 伺服器位址。

#### 1b. 要求密碼/授權碼

**直接在回覆文字中輸出純文字表格（不要包在 ``` 裡，不要調用任何工具）：**

範例：

🔐 安全驗證
─────────────────
提供商：[provider_name]
需要：[auth_label]
密碼 / 授權碼：__________________
─────────────────

請直接在下方對話框中輸入您的 [密碼/授權碼/應用專用密碼]。

使用者回覆後，執行連線測試：

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --test-connection \
  --sender "sender_email" \
  --smtp-server "smtp_server" \
  --smtp-port "smtp_port" \
  --ssl-mode "ssl_mode" \
  --password "使用者提供的密碼"
```

- **連線成功** → "驗證成功！" → 進入第 2 步。
- **連線失敗** → 用文字提示錯誤類型，引導重新輸入或回到 1a。

**安全提醒：密碼僅存在於當前對話的臨時變數中，不回顯。**


### 第 2 步：郵件撰寫（一頁純文字表格）

**核心設計：不是一個個問，而是直接在對話回覆中輸出純文字表格，所有欄位一次呈現。使用者一則訊息填完。對話不停頓。**

> **⚠️ 不要呼叫 `show_widget`！不要包 code block！** 直接在回覆文字中印出以下內容。

範例：

📧 填寫郵件
─────────────────
收件人：__________________（多個用逗號分隔）
抄送：__________________（選填，多個用逗號分隔）
暗送：__________________（選填，多個用逗號分隔）
主旨：__________________
內文：__________________（留空則由 AI 自動生成）
─────────────────

請直接在下方對話框中一則訊息填完以上所有欄位。範例：收件人：alice@example.com，主旨：季度報告，內文：請查收附件。

**解析使用者的回覆：**

```
to_addrs  = 解析收件人（逗號/分號分隔）
cc_addrs  = 解析抄送（可為空）
bcc_addrs = 解析暗送（可為空）
subject   = 主旨
body_text = 內文（可為空 → 由 AI 生成）
body_ai_generate = (body_text 為空時設為 True)
```

**驗證：**
- 收件人不可為空 → "收件人為必填欄位。"
- 主旨不可為空 → "主旨為必填欄位。"

**跳過條件**：若使用者在觸發時已提供部分資訊，於表格中對應欄位顯示已填值（取代底線），並告知「已預填部分欄位，請確認或補充。」

---

### 第 3 步：附件（點選方式）

使用 `AskUserQuestion` 讓使用者選擇是否附加檔案：

```json
{
  "questions": [{
    "question": "是否需要附加檔案？",
    "header": "附件",
    "options": [
      {"label": "不需要附件", "description": "純文字郵件，直接進入確認步驟"},
      {"label": "需要附加檔案", "description": "選擇後請在輸入框上傳檔案"}
    ]
  }]
}
```

**若選「不需要附件」：**
- `attachments = []`
- 直接進入第 4 步。

**若選「需要附加檔案」：**
- **停止對話**，告訴使用者：
  > "請在輸入框中上傳您要附加的檔案。上傳完成後，請回覆「完成」，
  > 我會繼續處理您的郵件。"
- 等待使用者上傳檔案並回覆「完成」。
- 收集使用者上傳的所有檔案路徑，存入 `attachments` 列表。
- 確認收到的檔案：
  > "已收到以下附件：
  > - [檔案1名稱]
  > - [檔案2名稱]
  > 將繼續生成郵件。"
- 進入第 4 步。

**如果使用者在觸發 skill 時已附帶了檔案：**
- 不再詢問，直接將已偵測到的檔案列入 `attachments`。
- 告知使用者"已偵測到對話中的檔案：[檔案列表]，將作為附件。"

---

### 第 4 步：生成與確認

**5a. 生成完整郵件內容**

若第 2 步中 `body_ai_generate` 為 True（使用者未填寫內文）：
- 此時才生成內文，因為現在已取得附件資訊。
- 根據以下資訊生成專業郵件內文：
  - 收件人（若已知其姓名/職位）
  - 郵件主旨
  - 附件內容（若有附件，可讀取附件內容或根據檔名推斷）
  - 對話上下文（使用者最初的需求）
  - 適當的問候語和結語
- 生成後保存為 `body_text`。

若使用者已自行填寫內文，直接使用。

**5b. 預覽**

執行預覽命令：

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --preview \
  --sender "sender_email" \
  --smtp-server "smtp_server" \
  --smtp-port "smtp_port" \
  --ssl-mode "ssl_mode" \
  --password "password" \
  --display-name "display_name" \
  --to "to_addrs" \
  --cc "cc_addrs" \
  --bcc "bcc_addrs" \
  --subject "subject" \
  --body "body_text" \
  --attach "file1" "file2"
```

若內文較長，可先寫入臨時檔案再使用 `--body-file`。

向使用者展示預覽結果，並使用 `AskUserQuestion` 請使用者確認：

```json
{
  "questions": [{
    "question": "請確認以下郵件內容是否正確無誤。",
    "header": "確認郵件",
    "options": [
      {"label": "確認並發送", "description": "核對無誤，立即發送郵件"},
      {"label": "修改", "description": "返回修改郵件內容（收件人、主旨、內文等）"},
      {"label": "捨棄", "description": "取消本次郵件發送"}
    ]
  }]
}
```

---

### 第 5 步：發送

**若使用者選「確認並發送」：**

執行發送命令（與預覽命令相同參數，移除 `--preview`）：

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --sender "sender_email" \
  --smtp-server "smtp_server" \
  --smtp-port "smtp_port" \
  --ssl-mode "ssl_mode" \
  --password "password" \
  --display-name "display_name" \
  --to "to_addrs" \
  --cc "cc_addrs" \
  --bcc "bcc_addrs" \
  --subject "subject" \
  --body "body_text" \
  --attach "file1" "file2"
```

**重要：發送命令的參數必須與預覽命令完全一致，不可修改任何值。**

- **發送成功**（輸出含 `SUCCESS`）：
  > "郵件已成功發送！
  > 收件人：[to_addrs]
  > 主旨：[subject]"

  **發送成功後，立即詢問是否保存寄件人資訊（使用 AskUserQuestion 按鍵）：**

  ```json
  {
    "questions": [{
      "question": "是否要保存本次寄件人資訊，以便下次直接使用（無需重新輸入郵箱與密碼）？",
      "header": "保存寄件人",
      "options": [
        {"label": "要，建立專屬技能", "description": "為您建立一個包含此寄件人資訊的個人專屬郵件技能"},
        {"label": "不要，以後再說", "description": "下次仍需重新輸入郵箱與密碼"}
      ]
    }]
  }
  ```

  - **若選「要」**：按照下方「用戶專屬技能建立流程」執行，創建 `CC-EmailSender-{用戶識別名}` 技能。
  - **若選「不要」**：流程正常結束。

- **發送失敗**（輸出含 `ERROR`）：
  根據錯誤類型處理：
  - 認證錯誤 → "發送時認證失敗，密碼可能已過期。請重新提供密碼/授權碼。"
  - 連線錯誤 → "無法連接 SMTP 伺服器，請檢查網路連線。"
  - 附件錯誤 → "附件檔案不存在：[檔案路徑]。請確認檔案路徑。"
  - 其他 → 顯示錯誤訊息，詢問是否重試。

**若使用者選「修改」：**
- 詢問要修改哪個部分：收件人/抄送/暗送/主旨/內文/附件。
- 回到第 2 步重新呈現表格（預填當前值），或回到第 3 步（若修改附件）。
- 修改後重新執行第 4 步預覽。

**若使用者選「捨棄」：**
- "已取消本次郵件發送。" 停止流程。

---

### 第 6 步：保存寄件人資訊（選用）

僅當第 5 步使用者選「要，建立專屬技能」時執行。

---

## 用戶專屬技能建立流程

**重要原則：永不修改原始的 CC-EmailSender 技能。專屬技能一律以新名稱獨立建立。**

### 觸發條件

觸發於第 5 步中使用者選擇「要，建立專屬技能」。

### 建立步驟

1. **決定技能名稱**：
   ```
   格式：CC-EmailSender-{用戶識別名}
   範例：CC-EmailSender-KuoWenhui
   ```
   用戶識別名由對話中已知的使用者姓名/帳號決定。若未知，使用郵箱 @ 前面的部分。

2. **使用 SkillManage 建立新技能**：
   呼叫 `SkillManage` 工具，command 為 `"create"`，提供以下內容：

   - **name**: `CC-EmailSender-{用戶識別名}`
   - **description**: "個人專屬郵件發送器 — {用戶郵箱}。無需重新輸入 SMTP 設定與密碼。"
   - **content (SKILL.md)**: 以 CC-EmailSender 的完整 SKILL.md 為基礎，進行以下修改：
     - 在最上方 frontmatter 之後新增一個「預設寄件人資訊」區塊（純變數，勿寫入密碼明文到說明文字中）
     - 將 `--detect-smtp` 步驟標記為「已設定，跳過」
     - 在 SMTP 命令的範本中，直接代入已儲存的 `sender_email`、`smtp_server`、`smtp_port`、`ssl_mode`、`password`、`display_name`
     - 在資料安全段落中增加備註：「此為個人專屬技能，寄件人資訊已預先設定。」

3. **建立完成後告知使用者**：
   > "已為您建立個人專屬郵件技能 **{技能名稱}**。今後您需要發信時，直接告訴我「用 {技能名稱} 發郵件」即可，無需再次輸入郵箱與密碼。"

### 專屬技能的使用流程

當用戶觸發專屬技能時，流程如下：
- **跳過第 1 步**（寄件人設定 — SMTP 與密碼已預設）
- 直接從 **第 2 步**（郵件撰寫表單）開始
- 後續步驟（附件、預覽、發送、保存）完全一致

---

## display_name（寄件人名稱）處理

寄件人顯示名稱為選填欄位。取得方式：
1. 若對話上下文中已知使用者姓名 → 自動使用。
2. 若未知 → 從郵箱地址的使用者名部分推斷，或留空。
3. 使用者可在修改步驟中指定。

---

## 資料安全

- **密碼不儲存於通用技能**：密碼/授權碼僅存在於當前對話的臨時變數中，對話結束即消失。
- **不回顯密碼**：在回覆中絕不顯示密碼內容。
- **通用技能無設定檔**：CC-EmailSender 不依賴任何持久化設定檔，SMTP 設定每次現場詢問。
- **多人安全**：不同使用者使用通用技能時不會互相影響，無殘留資料。
- **專屬技能安全提醒**：若使用者選擇建立個人專屬技能（`CC-EmailSender-{用戶名}`），寄件人資訊（含密碼/授權碼）將保存在該技能的 SKILL.md 中。請使用者自行評估風險，僅在信任環境中使用。

---

## 命令參考

### 偵測模式
```bash
python send_email.py --detect-smtp "EMAIL"
```

### 連線測試模式
```bash
python send_email.py --test-connection \
  --sender "EMAIL" --smtp-server "SERVER" --smtp-port "PORT" \
  --ssl-mode "ssl|starttls|none" --password "PWD"
```

### 預覽模式
```bash
python send_email.py --preview \
  --sender "EMAIL" --smtp-server "SERVER" --smtp-port "PORT" \
  --ssl-mode "ssl|starttls|none" --password "PWD" \
  --to "TO" --cc "CC" --bcc "BCC" \
  --subject "SUBJECT" --body "BODY" --attach "FILE1" "FILE2"
```

### 發送模式
```bash
python send_email.py \
  --sender "EMAIL" --smtp-server "SERVER" --smtp-port "PORT" \
  --ssl-mode "ssl|starttls|none" --password "PWD" \
  --to "TO" --cc "CC" --bcc "BCC" \
  --subject "SUBJECT" --body "BODY" --attach "FILE1" "FILE2"
```

### 參數清單

| 參數 | 必需 | 說明 |
|------|------|------|
| `--detect-smtp EMAIL` | 偵測模式 | 根據郵箱地址偵測 SMTP 設定 |
| `--test-connection` | 測試模式 | 測試 SMTP 連線和認證 |
| `--preview` | 預覽模式 | 僅預覽不發送 |
| `--sender EMAIL` | 發送/測試 | 寄件人郵箱 |
| `--smtp-server ADDR` | 發送/測試 | SMTP 伺服器位址 |
| `--smtp-port PORT` | 發送/測試 | SMTP 連接埠 |
| `--ssl-mode MODE` | 發送/測試 | 加密模式: ssl / starttls / none |
| `--password PWD` | 發送/測試 | 密碼/授權碼/應用專用密碼 |
| `--display-name NAME` | 選填 | 寄件人顯示名稱 |
| `--to EMAILS` | 發送 | 收件人（逗號分隔） |
| `--cc EMAILS` | 選填 | 抄送（逗號分隔） |
| `--bcc EMAILS` | 選填 | 暗送（逗號分隔） |
| `--subject TEXT` | 發送 | 郵件主旨 |
| `--body TEXT` | 發送 | 郵件內文 |
| `--body-file PATH` | 替代 | 從檔案讀取內文 |
| `--html` | 選填 | 標記內文為 HTML |
| `--attach FILES` | 選填 | 附件路徑（可多個） |

---

## 支援的郵箱提供商

| 提供商 | 域名 | SMTP 伺服器 | 連接埠 | 加密 | 認證方式 |
|--------|------|------------|--------|------|----------|
| Gmail | gmail.com | smtp.gmail.com | 465 | SSL | 應用專用密碼 |
| Outlook | outlook.com, hotmail.com, live.com | smtp-mail.outlook.com | 587 | STARTTLS | 密碼 |
| Office 365 | office365.com | smtp.office365.com | 587 | STARTTLS | 密碼 |
| 網易 163 | 163.com | smtp.163.com | 465 | SSL | 授權碼 |
| 網易 126 | 126.com | smtp.126.com | 465 | SSL | 授權碼 |
| 網易 Yeah | yeah.net | smtp.yeah.net | 465 | SSL | 授權碼 |
| 網易企業/靈犀 | qiye.163.com | smtphz.qiye.163.com | 465 | SSL | 密碼/授權碼 |
| QQ 郵箱 | qq.com | smtp.qq.com | 465 | SSL | 授權碼 |
| Foxmail | foxmail.com | smtp.qq.com | 465 | SSL | 授權碼 |
| 新浪 | sina.com | smtp.sina.com | 465 | SSL | 密碼 |
| 搜狐 | sohu.com | smtp.sohu.com | 465 | SSL | 密碼 |
| 阿里雲 | aliyun.com | smtp.qiye.aliyun.com | 465 | SSL | 密碼 |
| Yahoo | yahoo.com | smtp.mail.yahoo.com | 465 | SSL | 應用專用密碼 |
| iCloud | icloud.com | smtp.mail.me.com | 587 | STARTTLS | 應用專用密碼 |
| Zoho | zoho.com | smtp.zoho.com | 465 | SSL | 密碼 |
| 未知/企業域名 | * | 詢問使用者 | 詢問 | 詢問 | 詢問 |

完整 SMTP 設定參考見 `references/smtp_settings.md`。

---

## 資源

- `scripts/send_email.py` — 核心腳本（Python 標準庫，無外部依賴）
- `references/smtp_settings.md` — 各郵箱提供商 SMTP 設定參考
