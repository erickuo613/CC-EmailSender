# SMTP 伺服器設定參考

各郵箱提供商的 SMTP 設定，供手動設定時查詢。

---

## Gmail / Google Workspace

| 項目 | 值 |
|------|-----|
| SMTP 伺服器 | `smtp.gmail.com` |
| SSL 連接埠 | 465 |
| STARTTLS 連接埠 | 587 |
| 認證方式 | 應用專用密碼 (App Password) |

> **注意**：Gmail 不接受登入密碼透過 SMTP 登入。必須：
> 1. 啟用兩步驟驗證 (2FA)
> 2. 至 Google 帳戶 → 安全性 → 應用專用密碼 生成密碼
> 3. 使用該 16 位應用專用密碼（不含空格）作為 SMTP 密碼

---

## Outlook / Hotmail / Live / MSN

| 項目 | 值 |
|------|-----|
| SMTP 伺服器 | `smtp-mail.outlook.com` |
| STARTTLS 連接埠 | 587 |
| 認證方式 | 帳戶密碼 |

> 若已啟用兩步驟驗證，需使用應用專用密碼。

---

## Office 365

| 項目 | 值 |
|------|-----|
| SMTP 伺服器 | `smtp.office365.com` |
| STARTTLS 連接埠 | 587 |
| 認證方式 | 帳戶密碼 |

> 適用於 Office 365 商業版/企業版帳戶。若已啟用多因素驗證 (MFA)，需使用應用專用密碼。

---

## 網易個人郵箱 (163 / 126 / yeah.net / 188)

| 域名 | SMTP 伺服器 | SSL 連接埠 |
|------|------------|-----------|
| 163.com | `smtp.163.com` | 465 |
| 126.com | `smtp.126.com` | 465 |
| yeah.net | `smtp.yeah.net` | 465 |
| 188.com | `smtp.188.com` | 465 |

> **認證方式**：授權碼（非登入密碼）
> 1. 登入網頁版郵箱
> 2. 進入設定 → POP3/SMTP/IMAP
> 3. 開啟 SMTP 服務
> 4. 生成授權碼
> 5. 使用授權碼作為 SMTP 密碼

---

## 網易企業郵箱 / 靈犀

| 項目 | 值 |
|------|-----|
| SMTP 伺服器（華東） | `smtphz.qiye.163.com` |
| SMTP 伺服器（華北） | `smtp.qiye.163.com` |
| SSL 連接埠 | 465 / 994 |
| STARTTLS 連接埠 | 587 |
| 認證方式 | 登入密碼 或 授權碼 |

> - `hz` = 華東節點。不同地區可能使用不同前綴。
> - 部分企業部署需要授權碼而非登入密碼。
> - 若收到 `535 ERR.LOGIN.REQCODE` 錯誤，請至網頁郵箱 → 設定 → 客戶端設定 → 啟用 SMTP 並生成授權碼。

---

## QQ 郵箱 / Foxmail

| 域名 | SMTP 伺服器 | SSL 連接埠 |
|------|------------|-----------|
| qq.com | `smtp.qq.com` | 465 |
| foxmail.com | `smtp.qq.com` | 465 |
| vip.qq.com | `smtp.qq.com` | 465 |

> **認證方式**：授權碼（非登入密碼）
> 1. 登入 QQ 郵箱網頁版
> 2. 設定 → 帳戶 → POP3/SMTP 服務 → 開啟
> 3. 生成授權碼
> 4. 使用授權碼作為 SMTP 密碼

---

## 新浪郵箱

| 域名 | SMTP 伺服器 | SSL 連接埠 |
|------|------------|-----------|
| sina.com | `smtp.sina.com` | 465 |
| sina.cn | `smtp.sina.cn` | 465 |

> **認證方式**：帳戶密碼

---

## 搜狐郵箱

| 項目 | 值 |
|------|-----|
| SMTP 伺服器 | `smtp.sohu.com` |
| SSL 連接埠 | 465 |
| 認證方式 | 帳戶密碼 |

---

## 阿里雲郵箱

| 項目 | 值 |
|------|-----|
| SMTP 伺服器 | `smtp.qiye.aliyun.com` |
| SSL 連接埠 | 465 |
| 認證方式 | 帳戶密碼 |

---

## Yahoo 郵箱

| 域名 | SMTP 伺服器 | SSL 連接埠 |
|------|------------|-----------|
| yahoo.com | `smtp.mail.yahoo.com` | 465 |
| yahoo.com.tw | `smtp.mail.yahoo.com` | 465 |
| yahoo.com.hk | `smtp.mail.yahoo.com` | 465 |
| yahoo.co.jp | `smtp.mail.yahoo.co.jp` | 465 |

> **認證方式**：應用專用密碼
> 至 Yahoo 帳戶安全設定生成應用專用密碼。

---

## iCloud / Apple 郵箱

| 域名 | SMTP 伺服器 | STARTTLS 連接埠 |
|------|------------|----------------|
| icloud.com | `smtp.mail.me.com` | 587 |
| me.com | `smtp.mail.me.com` | 587 |
| mac.com | `smtp.mail.me.com` | 587 |

> **認證方式**：應用專用密碼
> 1. 登入 Apple ID 帳戶頁面
> 2. 進入帳戶 → 應用專用密碼
> 3. 生成密碼

---

## Zoho 郵箱

| 項目 | 值 |
|------|-----|
| SMTP 伺服器 | `smtp.zoho.com` |
| SSL 連接埠 | 465 |
| 認證方式 | 帳戶密碼 |

> 需在 Zoho 設定中啟用 SMTP 服務。

---

## ProtonMail

| 項目 | 值 |
|------|-----|
| SMTP 伺服器 | `127.0.0.1` (本地) |
| STARTTLS 連接埠 | 1031 |
| 認證方式 | Bridge 密碼 |

> ProtonMail 不直接支援 SMTP。需安裝 [Proton Mail Bridge](https://proton.me/mail/bridge)
> 本地客戶端，Bridge 會在本地架設 SMTP 伺服器。使用 Bridge 生成的密碼登入。

---

## 企業 / 自定義域名郵箱

若郵箱使用企業自有域名（如 `user@company.com`），無法自動偵測 SMTP 設定。
請向 IT 管理員確認以下資訊：

| 項目 | 詢問內容 |
|------|---------|
| SMTP 伺服器位址 | 如 `smtp.company.com` |
| 連接埠 | 通常 465 (SSL) 或 587 (STARTTLS) |
| 加密方式 | SSL / STARTTLS / 無 |
| 認證方式 | 登入密碼 / 授權碼 |
| 帳號格式 | 完整郵箱地址 或僅使用者名 |

---

## 加密方式說明

| 方式 | 連接埠 | 說明 |
|------|--------|------|
| SSL | 465 | 連線時直接加密，推薦使用 |
| STARTTLS | 587 | 先建立普通連線再升級為加密連線 |
| 無加密 | 25 | 不加密，不推薦，可能被 ISP 封鎖 |

---

## 認證方式總覽

| 類型 | 說明 | 適用提供商 |
|------|------|-----------|
| 帳戶密碼 | 使用網頁登入的密碼 | Outlook, Office365, 新浪, 搜狐, 阿里雲, Zoho |
| 授權碼 | 在郵箱設定中生成的專用密碼 | 網易 163/126/yeah, QQ, Foxmail |
| 應用專用密碼 | 需啟用兩步驟驗證後生成 | Gmail, iCloud, Yahoo |
| 密碼或授權碼 | 兩者皆可，視部署方式 | 網易企業郵箱/靈犀 |
| Bridge 密碼 | 本地 Bridge 客戶端生成 | ProtonMail |
