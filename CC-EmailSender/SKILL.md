---
name: CC-EmailSender
description: "Send emails via SMTP. This skill should be triggered whenever the user's intent involves sending or delivering content via email — not only when they use explicit keywords like '发邮件'. Examples: notifying someone, sharing a file or report with someone, sending meeting minutes, forwarding content, replying with a summary, or any request that implies 'get this to someone via email'. Supports: multiple sender profiles, password memory, contacts-based recipient selection (manual, persistent), AI-generated subject/body, CC/BCC, file attachments (from chat, local path, or AI-generated), preview before sending, plain text/HTML, UTF-8."
agent_created: true
---

# Email Sender v4

Multi-profile SMTP email tool with contacts management, AI-powered content generation,
smart skip (don't re-ask for what's already provided), and interactive step-by-step workflow.

## Prerequisites

- Python 3.x + standard library (no external packages).
- Config file: `~/.workbuddy/skills/CC-EmailSender/config/email_config.json`
- Password store: `~/.workbuddy/skills/CC-EmailSender/config/passwords.json`
- Contacts store: `~/.workbuddy/skills/CC-EmailSender/config/contacts.json`

## Script

```
~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py
```

---

## Trigger Policy

**DO NOT wait for explicit keywords.** Trigger this skill whenever the user's
request implies sending content to someone via email. Examples of triggering
intents (non-exhaustive):

| User says (examples) | Interpretation |
|---|---|
| "把这个报告发给王总" | Send the report to 王总 via email |
| "通知一下团队明天开会" | Email the team about tomorrow's meeting |
| "把这份记录邮件给 zhangsan@example.com" | Email the record |
| "帮我回复那封邮件，说收到" | Compose and send a reply email |
| "把这个文件分享给小张" | Email the file to 小张 |
| "给客户发一下报价单" | Email the quote to the client |

If the user's intent is ambiguous (could be email OR instant message OR other),
**ask** which channel they prefer before proceeding.

---

## Pre-Scan: Gather Everything Before You Start

**Before any interaction**, scan the user's message AND any files attached
to the conversation. Build a concrete **data map** — not just a boolean
check, but the actual values. This map is your single source of truth.

| Parameter | What to extract | Where to store it mentally |
|---|---|---|
| **Sender** | Email or name. Auto-select if only 1 profile. | `sender = "..."` |
| **To** | All mentioned recipients. | `to_list = [...]` |
| **CC** | Anyone mentioned with "抄送"/"cc". | `cc_list = [...]` |
| **BCC** | Anyone mentioned with "密送"/"bcc". | `bcc_list = [...]` |
| **Subject** | Topic from user message. | `subject = "..."` |
| **Body** | Message content from user message. | `body = "..."` |
| **Attachments** | **ALL files the user uploaded in chat, OR file paths mentioned, OR "生成X文件" requests.** Copy every detected path/name into a list. | `attachments = [...]` |

**CRITICAL rules**:
- **Attachments are NOT optional data.** If the user uploaded a file or
  mentioned a file path, you MUST record it in `attachments` immediately.
  Never lose this data — it is as important as the recipient address.
- **Do NOT skip recording just because a step will be "skipped"** — 
  "skip" means "don't ask the question again", NOT "discard the data".
- Only ask the user for parameters that have **empty/null values** after
  this scan. But even when you skip asking, the collected values MUST flow
  into the final send command.

---

## Interactive Workflow (Step by Step)

Collect only the **missing** parameters determined in the pre-scan.
All steps use either `AskUserQuestion` (for clickable choices) or plain
text questions (for free-form input). One step at a time — never batch.

### Step 0: Sender (click-to-select, skip if known)

Run `--list-profiles`:

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --list-profiles
```

Use `AskUserQuestion` with each profile as an option:

```json
{
  "questions": [{
    "question": "请选择寄件人邮箱：",
    "header": "寄件人",
    "options": [
      {"label": "郭世腾", "description": "rosemerry.wang@aife.cloud"},
      {"label": "新增寄件人", "description": "添加一个新的邮箱账户"}
    ]
  }]
}
```

- No profiles? Run `--init-config` then `--add-profile`, then re-list.
- "新增寄件人" → run `--add-profile`, then re-list.

**Skip if**: only one profile exists → auto-select it without asking.

### Step 1: Password (auto-loaded, skip always)

Password auto-loaded from `passwords.json`. Never mention it to the user.
If loading fails → the script reports the error at send time, not now.

### Step A: Recipient(s) / To (click-to-select, skip if known)

Run `--list-contacts` for the selected sender:

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --list-contacts "sender@email.com"
```

Use `AskUserQuestion` to present contacts as clickable options.
Include "其他" for manual input and "从联系人添加" option.

```json
{
  "questions": [{
    "question": "请选择收件人：",
    "header": "收件人",
    "options": [
      {"label": "郭文辉", "description": "kuo.wenhui@feg.cn"},
      {"label": "王小明", "description": "wangxm@company.com"},
      {"label": "其他", "description": "手动输入收件人邮箱"}
    ]
  }]
}
```

- No contacts? Show only "其他" and "管理联系人".
- "管理联系人" → run `--add-contact` to add a contact, then re-query.

**Skip if**: user already specified a recipient in their original message.

### Step B: CC / BCC (optional, skip if not needed)

Ask with `AskUserQuestion`:

```json
{
  "questions": [{
    "question": "需要抄送 (CC) 或密送 (BCC) 吗？",
    "header": "抄送/密送",
    "options": [
      {"label": "不需要", "description": "只发给收件人"},
      {"label": "添加抄送 (CC)", "description": "收件人可见抄送对象"},
      {"label": "添加密送 (BCC)", "description": "收件人不可见密送对象"},
      {"label": "两者都要", "description": "同时添加 CC 和 BCC"}
    ]
  }]
}
```

If user selects CC/BCC → for each, re-run `--list-contacts` and present
the same contact list format with `AskUserQuestion`. Support **multi-select**
(`multiSelect: true`) so the user can pick multiple contacts at once.
Include "其他" for manual input.

**Skip if**: user already specified CC/BCC in their original message,
or if the context clearly doesn't need it (short internal message, etc.).

### Step C: Subject (AI-generated options + manual)

Generate 3-5 subject line options based on:
- The recipient(s)
- The body content (if already known)
- The overall context of the user's request
- Current date / time if relevant

Present with `AskUserQuestion`:

```json
{
  "questions": [{
    "question": "请选择邮件主旨：",
    "header": "主旨",
    "options": [
      {"label": "【会议纪要】2026-07-09 项目进度同步", "description": "AI 生成"},
      {"label": "项目进度同步 - 会议纪要", "description": "AI 生成"},
      {"label": "今日会议记录，请查收", "description": "AI 生成"},
      {"label": "Re: 项目进度同步会议", "description": "AI 生成"},
      {"label": "自行输入", "description": "手动输入邮件主旨"}
    ]
  }]
}
```

Subjects should be:
- Professional and context-appropriate
- Include 【标签】 prefixes when useful (e.g. 【通知】【会议纪要】【报告】)
- 5-30 characters, concise

If user selects "自行输入" → prompt for free-text input.

**Skip if**: user already specified a clear subject in their original message.

### Step D: Body (three generation methods)

Present with `AskUserQuestion`:

```json
{
  "questions": [{
    "question": "如何生成邮件正文？",
    "header": "正文",
    "options": [
      {"label": "AI 自动生成 (推荐)", "description": "根据收件人和主旨自动撰写，生成后您可确认修改"},
      {"label": "使用模板", "description": "提供结构化模板，您填充关键信息"},
      {"label": "自行输入", "description": "手动输入或粘贴邮件正文"}
    ]
  }]
}
```

#### Option D1: AI 自动生成

Generate a complete, professional email body based on:
- Recipient name/role (from contacts or context)
- Selected subject
- Known context from the conversation
- Appropriate greeting and closing

Present the generated body to the user and ask for confirmation or edits:

```
以下是为您生成的邮件正文：

---
王总，您好：

以下是今日项目进度同步会议的纪要，请查收。

...

此致
郭世腾
---

是否满意？可以直接回复修改意见，或回复「确认」使用此正文。
```

Allow the user to refine: "把开头改成更正式一点", "加一段关于预算的说明", etc.

#### Option D2: 使用模板

Provide a structured template with placeholders. The user fills in the blanks:

```
请填充以下模板（回复时直接修改即可）：

---
[称呼]，您好：

[正文第一段 — 说明来意]

[正文第二段 — 详细内容]

[正文第三段 — 后续行动/截止日期]

此致
郭世腾
---
```

After user submits the filled template, use it as the body.

#### Option D3: 自行输入

Ask the user to type or paste the body content:

> "请输入邮件正文："

Wait for input. For long content, instruct the user they can also provide a file path.

**Skip if**: user already provided body content in their original message.

### Step E: Attachments (three sources)

**WARNING**: If the user already provided files (attached in chat, or
mentioned paths), do **NOT** ask "需要附加文件吗？" again. Instead,
immediately go to the **Data Assembly** step below — but MAKE SURE
every detected file path is loaded into your attachment list.

If the user has NOT provided any files, ask:

```json
{
  "questions": [{
    "question": "需要附加文件吗？",
    "header": "附件",
    "options": [
      {"label": "不需要", "description": "纯文本邮件，无附件"},
      {"label": "使用对话中的文件", "description": "您已上传到对话的文件"},
      {"label": "提供本地路径", "description": "指定本地文件路径作为附件"},
      {"label": "AI 生成", "description": "根据邮件内容自动生成附件（如报告、PDF）"}
    ]
  }]
}
```

#### Option E1: 使用对话中的文件

If the user already attached files in the chat, list them verbatim — do NOT
drop any:

```
对话中检测到以下文件：
- Meeting_Minutes_20260708.pdf    ← 用户上传的
- budget_summary.xlsx             ← 用户上传的
以上文件将全部作为附件。
如需移除某个文件，请回复文件名；否则回复「确认」。
```

**The default is: ALL detected files ARE included.** Only remove if the user
explicitly asks to exclude one.

#### Option E2: 提供本地路径

Ask for the file path(s) and verify each exists with `Read` or `Bash ls`.
Report missing files immediately. Do NOT proceed until all paths resolve.

#### Option E3: AI 生成

Generate the file based on:
- Recipient and subject
- Body content
- Any additional prompt from the user

Write the file to the workspace, then include it as an attachment.

**Skip the question if**: files were already detected in the Pre-Scan.
**But NEVER skip using the files.** Detected files always go into the
`--attach` parameter.

---

## MANDATORY: Data Assembly & Cross-Check (BEFORE preview)

**This step is NON-NEGOTIABLE.** Before running `--preview`, you MUST
verbally list every piece of data that will go into the send command.
This serves as a self-audit to catch dropped attachments, missing CC,
or other omissions.

Print this checklist in your reply:

```
【发送数据核对清单】
  ✅ 寄件人: <display_name> <<email>>
  ✅ 收件人: <list all to addresses>
  ✅ 抄送:   <list CC addresses, or "无">
  ✅ 密送:   <list BCC addresses, or "无">
  ✅ 主旨:   <subject>
  ✅ 正文:   <body preview (first 50 chars)>
  ✅ 附件:   <count> 个 — <file names>
```

Now compare this checklist against your Pre-Scan data map:

1. Is every file the user uploaded listed under 附件? **If not, add it now.**
2. Is every recipient the user mentioned listed under 收件人/抄送/密送?
3. Is the body text what the user actually wanted to send?

**If ANY item is missing from the checklist that the user provided, fix it
BEFORE proceeding to preview. Do NOT skip this step for any reason.**

Then and only then, proceed to the actual preview.

---

### Step F: Preview

Run `--preview` with all collected parameters, including `--cc` / `--bcc` / `--attach` as applicable:

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --sender "chosen@email.com" \
  --to "recipient@example.com" \
  --cc "cc1@example.com,cc2@example.com" \
  --bcc "bcc@example.com" \
  --subject "主旨" \
  --body "正文" \
  --attach "/path/to/file.pdf" \
  --preview
```

Show the preview output. If the body was written to a temp file, use `--body-file`.

### Step G: Confirm & Send (MANDATORY — never skip)

**UNDER NO CIRCUMSTANCES may you send the email without explicit user
confirmation.** Even if all data looks perfect, even if the user seems
certain, you MUST ask. This is the final safety net.

```json
{
  "questions": [{
    "question": "确认发送以上邮件吗？请核对收件人、主旨、正文和附件是否无误。",
    "header": "确认发送",
    "options": [
      {"label": "确认发送", "description": "核对无误，立即发送邮件"},
      {"label": "修改内容", "description": "返回修改邮件内容"},
      {"label": "取消", "description": "取消本次发送"}
    ]
  }]
}
```

- "确认发送" → run the same command **without `--preview`** (copy the
  exact same `--sender`, `--to`, `--cc`, `--bcc`, `--subject`, `--body`,
  `--attach` parameters from the preview command — do NOT alter them)
- "修改内容" → go back and ask which part to modify, rinse and repeat
  from the affected step
- "取消" → acknowledge and stop, do NOT send

On success: report briefly. On error, read the message and suggest fixes:
- Auth error → wrong password / need auth code (guide to webmail settings)
- Connection error → check SMTP server/port
- Attachment not found → verify file path

---

## Management Commands

| Command | Purpose |
|---------|---------|
| `--init-config` | Create empty profiles config |
| `--add-profile` | Interactively add a new sender email |
| `--list-profiles` | List all configured senders (JSON) |
| `--add-contact` | Interactively add a contact (use `--sender` to scope to one account) |
| `--list-contacts SENDER` | List all contacts for a sender (JSON) |

## Sending Commands

| Flag | Description |
|------|-------------|
| `--sender S` | Email address to send FROM (required) |
| `--to R` | Recipient(s), comma-separated (required) |
| `--subject S` | Subject line (required) |
| `--body B` | Body text (required unless `--body-file`) |
| `--body-file F` | Read body from file |
| `--html` | Body is HTML |
| `--cc A,B` | CC recipients |
| `--bcc A,B` | BCC recipients |
| `--attach F1 F2` | File paths to attach |
| `--password P` | Password (omit to auto-load; use "ask" to prompt) |
| `--preview` | Show preview only, do NOT send |

## Config Format

`email_config.json`:
```json
{
  "profiles": [
    {
      "email": "user@company.com",
      "display_name": "User Name",
      "smtp_server": "smtphz.qiye.163.com",
      "smtp_port": 465,
      "use_ssl": true
    }
  ]
}
```

`passwords.json` (separate file, NEVER commit or share):
```json
{
  "user@company.com": "their_password_or_auth_code"
}
```

`contacts.json` (manually maintained per sender):
```json
{
  "user@company.com": [
    {"name": "张三", "email": "zhangsan@example.com"},
    {"name": "李四", "email": "lisi@example.com"}
  ]
}
```

## Security Notes

- Passwords stored separately from profiles in `passwords.json`.
- All config files live in `~/.workbuddy/skills/CC-EmailSender/config/`.
- Passwords are plaintext — inform users of this trade-off.
- Never log or echo passwords in replies.
- Before sharing the skill zip, remove `config/` directory contents.

## Resources

- `scripts/send_email.py` — Main script
- `references/smtp_settings.md` — SMTP settings for common providers
- `assets/email_config_template.json` — Config template
