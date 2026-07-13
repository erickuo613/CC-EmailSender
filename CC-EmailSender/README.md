# 通用郵件發送器 — WorkBuddy 郵件發送技能

## 簡介

通用郵件發送器是一個 WorkBuddy 技能，讓你在對話中直接發送電子郵件。支援所有主流郵箱提供商（Gmail、Outlook、Office365、網易、QQ、iCloud、Yahoo 等），無需預先配置。

**核心特性：**

- **汎用相容** — 支援 Gmail、Outlook、網易(163/126/yeah/企業/靈犀)、QQ、iCloud、Yahoo 等所有電子郵件系統
- **自動偵測** — 根據郵箱地址自動識別提供商並帶入 SMTP 設定
- **無設定檔** — 不依賴任何持久化設定，每次使用時現場詢問，適合多人共用
- **互動式表單** — 所有使用者輸入均透過 `AskUserQuestion` 工具提供互動式輸入框，支援快捷選項與自定義填寫
- **AI 智能生成內文** — 可選擇由 AI 根據主旨和附件自動生成專業郵件內文，或自行填寫
- **附件支援** — 點選方式選擇是否附加檔案
- **發送前確認** — 預覽完整郵件後才發送，支援確認/修改/捨棄
- **連線驗證** — 發送前先測試 SMTP 連線，確保認證有效
- **個人專屬技能** — 發送成功後可選擇建立個人專屬技能，下次免重新輸入郵箱與密碼
- **安全無痕** — 密碼不儲存、不回顯，對話結束即消失

## 安裝

將整個 `CC-EmailSender` 資料夾放到 `~/.workbuddy/skills/` 目錄下。

## 使用方式

### 自然語言觸發

只要意圖是「把某內容透過郵件發送給某人」，就會自動激活：

| 你說的話 | 效果 |
|---------|------|
| "把這個報告發給王總" | 自動激活，進入郵件撰寫流程 |
| "通知團隊明天開會" | 自動激活，AI 生成內文 |
| "把這份 PDF 郵件給 zhangsan@example.com" | 自動激活，PDF 作為附件 |
| "幫我回覆那封郵件，說已收到" | 自動激活，生成回覆郵件 |

### 完整流程（6 步）

```
第 1 步：寄件人設定 — 判斷是否已提供郵箱 → 自動偵測 SMTP → 輸入密碼/授權碼 → 測試連線
第 2 步：互動式表單撰寫郵件（收件人/抄送/暗送/主旨 + 內文 AI 生成或自行填寫）
第 3 步：附件（點選是否附加）
第 4 步：生成完整郵件 → 預覽 → 確認/修改/捨棄
第 5 步：發送 → 詢問是否建立個人專屬技能
第 6 步：保存寄件人資訊（選用）
```

#### 第 1 步：寄件人設定

**1a. 判斷寄件人郵箱**

系統首先掃描使用者的觸發訊息，判斷是否已包含郵箱地址：

- **已提供郵箱** → 直接使用，跳過詢問，立即執行 SMTP 偵測
- **未提供郵箱** → 透過 `AskUserQuestion` 提供互動式輸入框，包含 Gmail / 網易QQ / Outlook 三個快捷選項，使用者點選後透過底部 **Other 自定義輸入框** 輸入完整郵箱地址

**1a-偵測：SMTP 自動偵測**

取得郵箱後，系統自動偵測所屬提供商和 SMTP 設定：

- `@gmail.com` → Gmail（需應用專用密碼）
- `@outlook.com` / `@hotmail.com` → Outlook（需帳戶密碼）
- `@163.com` / `@126.com` → 網易（需授權碼）
- `@qiye.163.com` → 網易企業郵箱/靈犀（需密碼或授權碼）
- `@qq.com` → QQ 郵箱（需授權碼）
- `@icloud.com` → iCloud（需應用專用密碼）
- 未知域名 → 透過 `AskUserQuestion` 讓使用者選擇加密方式（SSL/STARTTLS/不加密）並提供 SMTP 伺服器位址

**1b. 取得密碼/授權碼**

透過 `AskUserQuestion` 提供輸入框，包含三個認證方式選項：

| 選項 | 適用提供商 | 取得方式 |
|------|-----------|---------|
| 授權碼 | 網易/QQ | 網頁郵箱 → 設定 → POP3/SMTP/IMAP → 開啟 → 生成授權碼 |
| 應用專用密碼 | Gmail/iCloud/Yahoo | 帳戶設定 → 安全性 → 兩步驟驗證 → 應用專用密碼 |
| 登入密碼 | Outlook/企業郵箱 | 直接使用登入密碼 |

使用者點選對應選項後，透過 **Other 自定義輸入框** 輸入密碼/授權碼。系統立即測試 SMTP 連線，確認認證有效後才進入下一步。

#### 第 2 步：互動式表單撰寫

**2a. 郵件基本欄位**

透過 `AskUserQuestion` 一次提供 4 個互動式輸入框，使用者可同時填寫：

| 欄位 | 必填 | 快捷選項 | 自定義輸入 |
|------|------|---------|-----------|
| 收件人 | 是 | 稍後補充 | 透過 Other 輸入（多個用逗號分隔） |
| 抄送 | 否 | 不抄送 | 透過 Other 輸入（多個用逗號分隔） |
| 暗送 | 否 | 不暗送 | 透過 Other 輸入（多個用逗號分隔） |
| 主旨 | 是 | 由 AI 建議 | 透過 Other 輸入 |

**2b. 內文撰寫方式**

接著透過 `AskUserQuestion` 提供兩個選項：

- **AI自動生成(根據主旨與附件)** — 由 AI 根據主旨與附件內容自動生成專業郵件內文
- **自行填寫** — 透過 Other 自定義輸入框填寫郵件內文

若使用者在觸發時已提供部分資訊（如收件人郵箱、主旨等），系統會在對應欄位中預填已填值作為預設選項。

#### 第 3 步：附件

透過 `AskUserQuestion` 讓使用者選擇是否附加檔案：

- **不需要附件** → 直接進入確認步驟
- **需要附加檔案** → 系統暫停，使用者在輸入框上傳檔案後回覆「完成」

若使用者在觸發 skill 時已附帶檔案，系統直接將已偵測到的檔案列為附件，不再詢問。

#### 第 4 步：生成與確認

- 若使用者選擇 AI 生成內文 → 此時根據主旨、附件內容、對話上下文生成專業郵件內文
- 若使用者已自行填寫內文 → 直接使用
- 顯示完整郵件預覽
- 透過 `AskUserQuestion` 提供三個選項：**確認並發送** / **修改** / **捨棄**

#### 第 5 步：發送

確認後立即發送。發送成功會顯示收件人、主旨等摘要。

發送成功後，系統會詢問是否建立個人專屬技能：
- **要，建立專屬技能** → 建立 `CC-EmailSender-{用戶名}` 個人專屬技能，下次發信免重新輸入郵箱與密碼
- **不要，以後再說** → 流程結束

#### 第 6 步：保存寄件人資訊（選用）

僅當第 5 步使用者選擇建立專屬技能時執行。系統以原始 CC-EmailSender 為基礎，建立包含預設寄件人資訊的個人專屬技能。今後使用該專屬技能時，流程直接從第 2 步（互動式表單）開始。

## CLI 直接使用

也可以跳過互動流程，直接用命令列操作：

### 偵測 SMTP 設定

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --detect-smtp "user@gmail.com"
```

### 測試連線

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --test-connection \
  --sender "user@gmail.com" \
  --smtp-server "smtp.gmail.com" --smtp-port 465 --ssl-mode ssl \
  --password "app_password"
```

### 預覽郵件

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --preview \
  --sender "user@gmail.com" \
  --smtp-server "smtp.gmail.com" --smtp-port 465 --ssl-mode ssl \
  --password "app_password" \
  --to "recipient@example.com" \
  --subject "測試郵件" \
  --body "這是測試內容"
```

### 發送郵件

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --sender "user@gmail.com" \
  --smtp-server "smtp.gmail.com" --smtp-port 465 --ssl-mode ssl \
  --password "app_password" \
  --to "recipient@example.com" \
  --cc "cc@example.com" \
  --bcc "bcc@example.com" \
  --subject "報告" \
  --body "請查收附件" \
  --attach "/path/to/report.pdf" "/path/to/image.png"
```

## CLI 參數完整參考

### 模式選擇

| 參數 | 說明 |
|------|------|
| `--detect-smtp EMAIL` | 根據郵箱地址偵測 SMTP 設定（輸出 JSON） |
| `--test-connection` | 測試 SMTP 連線和認證（不發送郵件） |
| `--preview` | 僅預覽郵件，不實際發送 |

### SMTP 連線參數

| 參數 | 必需 | 說明 |
|------|------|------|
| `--sender EMAIL` | 是 | 寄件人郵箱地址 |
| `--smtp-server ADDR` | 是 | SMTP 伺服器位址 |
| `--smtp-port PORT` | 是 | SMTP 連接埠 |
| `--ssl-mode MODE` | 是 | 加密模式：`ssl` / `starttls` / `none` |
| `--password PWD` | 是 | 密碼/授權碼/應用專用密碼 |
| `--display-name NAME` | 否 | 寄件人顯示名稱 |

### 郵件內容參數

| 參數 | 必需 | 說明 |
|------|------|------|
| `--to EMAILS` | 是 | 收件人（逗號分隔） |
| `--cc EMAILS` | 否 | 抄送（逗號分隔） |
| `--bcc EMAILS` | 否 | 暗送（逗號分隔） |
| `--subject TEXT` | 是 | 郵件主旨 |
| `--body TEXT` | 是¹ | 郵件內文 |
| `--body-file PATH` | 是¹ | 從檔案讀取內文 |
| `--html` | 否 | 標記內文為 HTML 格式 |
| `--attach FILES` | 否 | 附件檔案路徑（可多個） |

> ¹ `--body` 和 `--body-file` 二選一。

## 目錄結構

```
CC-EmailSender/
├── README.md                           ← 本文件
├── SKILL.md                            ← 技能主文件（WorkBuddy 讀取）
├── scripts/
│   └── send_email.py                   ← 核心發送腳本（Python 標準庫，無外部依賴）
├── references/
│   └── smtp_settings.md                ← 各郵箱提供商 SMTP 設定參考
├── config/                             ← 設定檔目錄（泛用版為空，運行時自動生成）
│   ├── contacts.json                   ← 聯絡人（初始為空 {}）
│   ├── email_config.json               ← 郵箱設定（初始為空 {"profiles": []}）
│   ├── frequent_recipients.json        ← 常用收件人（初始為空 {}）
│   └── passwords.json                  ← 密碼（初始為空 {}）
└── assets/                             ← 模板與資源
```

## 安全注意事項

- **密碼不儲存** — 密碼/授權碼僅存在於當前對話中，對話結束即消失。不寫入任何檔案。
- **不回顯密碼** — 助手在對話中不會顯示密碼內容。
- **連線先驗證** — 發送前先測試 SMTP 連線，確認認證有效。
- **多人安全** — 不同使用者使用時不會互相影響，無殘留資料。
- **SSL/TLS 加密** — 所有 SMTP 連線使用 SSL 或 STARTTLS 加密。
- **專屬技能安全提醒** — 若使用者選擇建立個人專屬技能，寄件人資訊（含密碼/授權碼）將保存在該技能的 SKILL.md 中。請自行評估風險，僅在信任環境中使用。

## 常見問題

### Q: 發送失敗，提示「認證失敗」

密碼或授權碼錯誤。確認：
- Gmail → 使用應用專用密碼，非登入密碼（需先啟用兩步驟驗證）
- 網易 163/126 → 使用授權碼，非登入密碼
- QQ 郵箱 → 使用授權碼，非登入密碼
- Outlook → 使用帳戶密碼（若啟用兩步驗證則用應用專用密碼）
- 網易企業郵箱 → 先試登入密碼，若報 `ERR.LOGIN.REQCODE` 則生成授權碼

### Q: 發送失敗，提示「無法連接 SMTP 伺服器」

- 檢查 SMTP 伺服器位址和連接埠是否正確
- 公司網路可能封鎖 SMTP 連接埠，嘗試切換網路或聯繫 IT
- 確認加密方式是否正確（SSL 用 465，STARTTLS 用 587）

### Q: 我的郵箱域名無法自動識別

企業或自定義域名郵箱需要手動提供 SMTP 設定。系統會透過互動式輸入框讓你選擇加密方式並輸入 SMTP 伺服器位址。請向 IT 管理員確認：
- SMTP 伺服器位址
- 連接埠（通常 465 或 587）
- 加密方式（SSL 或 STARTTLS）
- 認證方式（密碼或授權碼）

### Q: 可以發給多個收件人嗎？

可以。在收件人輸入框中用逗號分隔多個郵箱地址。

### Q: 不想要 AI 生成內文，可以嗎？

可以。在內文撰寫方式中選擇「自行填寫」，透過 Other 自定義輸入框填寫你想要的內容即可。

### Q: 什麼是個人專屬技能？

發送成功後，系統會詢問你是否建立個人專屬技能。若選擇建立，系統會以你的寄件人資訊（郵箱、SMTP 設定、密碼）建立一個專屬技能（如 `CC-EmailSender-RosemerryWang`）。下次發信時直接使用該技能，流程從填寫郵件內容開始，免重新輸入郵箱與密碼。

### Q: 依賴什麼？

僅依賴 **Python 3 標準庫**（`smtplib`、`email`、`json`、`argparse`、`ssl`），無需安裝任何第三方套件。
