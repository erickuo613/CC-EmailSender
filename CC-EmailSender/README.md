# Email Sender — WorkBuddy SMTP 邮件发送技能

## 简介

Email Sender 是一个 WorkBuddy 技能，让你在对话中直接发送电子邮件。只需用自然语言描述你的需求（如「把这个报告发给王总」），无需记住特定命令。

**核心特性：**

- **自然语言触发** — 不需要说「发邮件」，任何隐含邮件发送意图的请求都会自动激活（如「通知团队」「把这个发给张三」）
- **多账户管理** — 支持配置多个寄件人邮箱，点击切换
- **密码记忆** — 每个账户的密码/授权码单独存储，一次输入，持续使用
- **联系人管理** — 为每个寄件人账户维护联系人列表，选择收件人时从联系人中点选
- **点选交互** — 寄件人、收件人（含 CC/BCC）、主旨选项、正文生成方式、确认发送均为点击选择
- **AI 智能生成** — 根据收件人和上下文自动生成主旨选项和邮件正文，减少打字
- **智能跳过** — 如果你在请求中已提供某些信息（收件人、标题、内容），不会重复询问
- **发送前预览** — 确认无误后再寄出
- **纯文本 / HTML** — 支持两种邮件格式
- **附件三来源** — 对话文件 / 本地路径 / AI 生成
- **CC / BCC** — 支持抄送和密送，可从联系人列表多选
- **完整 Unicode 支持** — 中文主旨和正文正常显示

## 安装

### 方式一：从 zip 包导入

拿到的 `CC-EmailSender.zip`，在 WorkBuddy 中通过 **技能管理面板 → 导入技能** 安装。

### 方式二：开发者手动部署

将整个 `CC-EmailSender` 文件夹放到 `~/.workbuddy/skills/` 目录下。

## 首次配置

### 1. 初始化配置文件

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --init-config
```

此命令在 `~/.workbuddy/skills/CC-EmailSender/config/` 下创建 `email_config.json`。

### 2. 添加寄件人邮箱

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --add-profile
```

按提示依次输入：

| 提示 | 说明 | 示例 |
|------|------|------|
| Email 地址 | 完整邮箱地址 | `zhangsan@company.com` |
| 显示名称 | 收件人看到的发件人名称 | `张三` |
| SMTP 服务器 | 发信服务器地址 | `smtphz.qiye.163.com` |
| SMTP 端口 | 端口号 | `465` |
| 使用 SSL? | 通常选 Y | `Y` |
| 是否保存密码? | 推荐选 y | `y` |

> **常用 SMTP 设置参考：** 见 `references/smtp_settings.md`，覆盖网易企业邮箱、163/126、Gmail、Outlook、QQ 邮箱等常见服务商。

### 3. 添加联系人（推荐）

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --add-contact --sender "你的邮箱"
```

按提示输入联系人姓名和邮箱。可重复执行添加多个联系人。管理命令：

```bash
# 查看某寄件人的所有联系人
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --list-contacts "你的邮箱"
```

### 4. 完成

配置完成后，直接用自然语言对助手说出你的邮件需求即可。

## 使用方式

### 自然语言触发

本技能不限于「发邮件」这类关键词。只要你的意图是「把某内容通过邮件发送给某人」，就会自动激活。例如：

| 你说的话 | 效果 |
|---------|------|
| 「把这个报告发给王总」 | 自动激活，收集缺失参数后发送 |
| 「通知一下团队明天开会」 | 自动激活，AI 生成主旨和正文 |
| 「把这份 PDF 邮件给 zhangsan@example.com」 | 自动激活，PDF 作为附件 |
| 「帮我回复那封邮件，说已收到」 | 自动激活，生成回复邮件 |

意图不明确时（邮件还是即时消息？），助手会先确认渠道。

### 智能跳过

如果你在请求中已经提供了部分信息，助手**不会重复询问**。例如你说「把这个报告发给王总，标题写项目进度更新」，那么收件人和主旨已经确定，只需要补全正文和附件。

### 交互式流程

流程按需执行，不一定走完所有步骤：

```
Step 0: 点选寄件人           ← 仅一个账户时自动跳过
Step 1: (密码自动读取)       ← 始终跳过
Step A: 点选收件人 (来自联系人) ← 已指定则跳过
Step B: 抄送/密送 (可选)     ← 通常跳过
Step C: AI 生成主旨选项      ← 已指定则跳过
Step D: 正文生成方式 (三选一)  ← 已指定则跳过
Step E: 附件 (三来源)        ← 已指定则跳过
Step F: 预览确认
Step G: 点选确认发送
```

### 正文的三种生成方式

| 方式 | 说明 |
|------|------|
| **AI 自动生成** | 根据收件人、主旨、上下文自动撰写专业邮件，生成后可修改 |
| **使用模板** | 提供结构化模板（称呼/正文/结语），你填充关键信息 |
| **自行输入** | 直接输入或粘贴正文内容 |

### 附件的三种来源

| 来源 | 说明 |
|------|------|
| **对话中的文件** | 你在对话中上传的文件，自动识别为候选附件 |
| **本地文件路径** | 指定本地文件路径，脚本验证后附加 |
| **AI 生成** | 根据邮件内容自动生成文件（如报告、摘要 PDF） |

### 命令行直接发送

也可以跳过交互流程，用 CLI 直接发送：

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --sender "你的邮箱" \
  --to "收件人@example.com" \
  --subject "邮件标题" \
  --body "邮件正文"
```

### 命令行：带 CC/BCC

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --sender "你的邮箱" \
  --to "recipient@example.com" \
  --cc "cc1@example.com,cc2@example.com" \
  --bcc "bcc@example.com" \
  --subject "通知" \
  --body "正文内容"
```

### 命令行：带附件

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --sender "你的邮箱" \
  --to "收件人@example.com" \
  --subject "报告" \
  --body "请查收附件" \
  --attach "/path/to/report.pdf" "/path/to/image.png"
```

### 命令行：预览（不发送）

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py \
  --sender "你的邮箱" \
  --to "收件人@example.com" \
  --subject "测试" \
  --body "内容" \
  --preview
```

输出示例：

```
==================================================
【邮件预览】
  发件人: 郭世腾 <rosemerry.wang@aife.cloud>
  收件人: kuo.wenhui@feg.cn
  抄送:   wangxm@company.com
  主旨:   测试
  格式:   纯文本  (2 字符)
--------------------------------------------------
内容
==================================================
(预览模式 — 邮件未实际发送)
```

## CLI 参数完整参考

### 管理命令

| 参数 | 说明 |
|------|------|
| `--init-config` | 创建空的 profiles 配置文件 |
| `--add-profile` | 交互式新增寄件人邮箱 |
| `--list-profiles` | 列出所有已配置的寄件人（JSON） |
| `--add-contact` | 交互式新增联系人（配合 `--sender` 指定归属账户） |
| `--list-contacts EMAIL` | 列出某寄件人的所有联系人（JSON） |
| `--config PATH` | 指定自定义配置文件路径 |

### 发送参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `--sender EMAIL` | 是 | 选择寄件人邮箱 |
| `--to EMAIL1,EMAIL2` | 是 | 收件人，多个用逗号分隔 |
| `--subject TEXT` | 是 | 邮件主旨 |
| `--body TEXT` | 是¹ | 邮件正文 |
| `--body-file PATH` | 是¹ | 从文件读取正文 |
| `--html` | 否 | 标记正文为 HTML 格式 |
| `--cc EMAIL1,EMAIL2` | 否 | 抄送收件人 |
| `--bcc EMAIL1,EMAIL2` | 否 | 密送收件人 |
| `--attach FILE1 FILE2` | 否 | 附件文件路径 |
| `--password PWD` | 否 | 密码（留空自动从密码库读取） |
| `--preview` | 否 | 仅预览，不实际发送 |

> ¹ `--body` 和 `--body-file` 二选一。

## 配置文件说明

技能使用 `~/.workbuddy/skills/CC-EmailSender/config/` 下的三个 JSON 文件：

### email_config.json — 邮箱账户配置

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

### passwords.json — 密码存储（独立文件）

```json
{
  "user@company.com": "auth_code_or_password"
}
```

> 密码与账户配置分离存储，便于分享技能时保护隐私。

### contacts.json — 联系人列表（手动维护）

```json
{
  "user@company.com": [
    {"name": "张三", "email": "zhangsan@example.com"},
    {"name": "李四", "email": "lisi@example.com"}
  ]
}
```

> 每个寄件人账户独立维护联系人列表。通过 `--add-contact` 命令添加，`--list-contacts` 查看。

## 目录结构

```
CC-EmailSender/
├── README.md                           ← 本文件
├── SKILL.md                            ← 技能主文件（WorkBuddy 读取）
├── scripts/
│   └── send_email.py                   ← 核心发送脚本（Python 标准库，无外部依赖）
├── references/
│   └── smtp_settings.md                ← 各邮件服务 SMTP 设置参考
├── assets/
│   ├── email_config_template.json      ← 邮箱配置模板
│   └── contacts_template.json          ← 联系人配置模板
└── config/                             ← 运行时配置（分享前请清空）
    ├── email_config.json               ← 邮箱账户配置
    ├── passwords.json                  ← 密码存储（敏感）
    └── contacts.json                   ← 联系人列表
```

## 安全注意事项

- **密码明文存储。** `passwords.json` 中的密码/授权码以明文保存。这是为便利性做的权衡——如果你对安全性有更高要求，可以选择不保存密码，每次发信时手动输入（CLI 模式使用 `--password ask`）。
- **分发技能 zip 时**，请确认 `config/` 目录下的文件不包含敏感信息（密码、授权码等）。建议分享前清空或删除 `config/` 目录内容。
- **密码文件权限**：建议将 `config/` 目录权限设置为仅当前用户可读。
- 助手对话中不会回显或记录密码信息。

## 常见问题

### Q: 发送失败，提示「认证失败 / Authentication failed」

密码或授权码错误。确认：
- 网易企业邮箱 → 部分部署需要授权码而非登录密码（若报 `ERR.LOGIN.REQCODE`，请去网页邮箱设置生成授权码）
- 网易个人邮箱 (163/126) → 必须使用授权码
- Gmail → 必须使用应用专用密码
- QQ 邮箱 → 必须使用授权码

### Q: 发送失败，提示「无法连接 SMTP 服务器」

- 检查 SMTP 服务器地址和端口是否正确
- 公司网络可能封锁了 SMTP 端口，尝试切换网络或联系 IT

### Q: 如何切换寄件人？

下次发邮件时，第一步就会列出所有已配置的寄件人供你点选。如果只有一个账户则自动选择。

### Q: 如何添加联系人？

在终端执行：

```bash
python ~/.workbuddy/skills/CC-EmailSender/scripts/send_email.py --add-contact --sender "你的邮箱"
```

或在交互流程中选「管理联系人」。

### Q: 联系人列表为什么是空的？

联系人需要手动添加，不会自动学习。首次使用前请用 `--add-contact` 导入常用联系人。

### Q: 能发给多个收件人吗？

可以。CLI 模式用逗号分隔：`--to "a@x.com,b@x.com"`。交互模式支持从联系人列表多选。

### Q: 不想要 AI 生成的内容，可以吗？

可以。主旨步骤选择「自行输入」，正文步骤选择「自行输入」，完全跳过 AI 生成。

### Q: 依赖什么？

仅依赖 **Python 3 标准库**（`smtplib`、`email`、`json`、`argparse`、`ssl`），无需安装任何第三方包。

## 开发与贡献

脚本位于 `scripts/send_email.py`。如需扩展功能：

- 添加新的 SMTP 服务商支持 → 更新 `references/smtp_settings.md`
- 修改交互流程 → 更新 `SKILL.md` 中的 Step 0-G
- 添加新 CLI 参数 → 修改 `send_email.py` 中的 `argparse` 部分

验证技能结构：

```bash
python ~/.workbuddy/skills/skill-creator/scripts/quick_validate.py \
  ~/.workbuddy/skills/CC-EmailSender
```

重新打包：

```bash
python ~/.workbuddy/skills/skill-creator/scripts/package_skill.py \
  ~/.workbuddy/skills/CC-EmailSender \
  /path/to/output/dir
```
