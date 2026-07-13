#!/usr/bin/env python3
"""
Universal Email Sender -- runtime-only SMTP email tool.

No config files. No persisted profiles. No password storage.
Every parameter is supplied at runtime via CLI arguments.

Supports:
  - Auto-detect SMTP provider from email domain (--detect-smtp)
  - Test SMTP connection before sending (--test-connection)
  - Preview before sending (--preview)
  - Plain text and HTML body
  - Multiple recipients (To, CC, BCC)
  - File attachments
  - Unicode subject and body (UTF-8)
  - SSL (port 465) and STARTTLS (port 587)

Usage:
  # Detect SMTP settings from email domain
  python send_email.py --detect-smtp user@gmail.com

  # Test connection
  python send_email.py --test-connection \
    --sender user@gmail.com \
    --smtp-server smtp.gmail.com --smtp-port 465 --ssl-mode ssl \
    --password "app_password"

  # Preview
  python send_email.py --preview \
    --sender user@gmail.com \
    --smtp-server smtp.gmail.com --smtp-port 465 --ssl-mode ssl \
    --password "app_password" \
    --to "recipient@example.com" \
    --subject "Test" --body "Hello"

  # Send
  python send_email.py \
    --sender user@gmail.com \
    --smtp-server smtp.gmail.com --smtp-port 465 --ssl-mode ssl \
    --password "app_password" \
    --to "recipient@example.com" \
    --subject "Test" --body "Hello"
"""

import sys
import io
import argparse
import json
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ============================================================
#  SMTP Provider Database
# ============================================================

SMTP_PROVIDERS = {
    # --- Gmail ---
    "gmail.com": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "app_password",
        "provider_name": "Gmail",
        "auth_label": "應用專用密碼 (App Password)",
        "instructions": "Gmail 需要應用專用密碼，非登入密碼。請至 Google 帳戶 > 安全性 > 兩步驟驗證 > 應用專用密碼 生成。",
    },
    "googlemail.com": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "app_password",
        "provider_name": "Gmail",
        "auth_label": "應用專用密碼 (App Password)",
        "instructions": "Gmail 需要應用專用密碼，非登入密碼。請至 Google 帳戶 > 安全性 > 兩步驟驗證 > 應用專用密碼 生成。",
    },

    # --- Outlook / Hotmail / Live / MSN ---
    "outlook.com": {
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "password",
        "provider_name": "Outlook",
        "auth_label": "帳戶密碼",
        "instructions": "使用 Outlook 帳戶密碼登入。若已啟用兩步驟驗證，請使用應用專用密碼。",
    },
    "hotmail.com": {
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "password",
        "provider_name": "Outlook (Hotmail)",
        "auth_label": "帳戶密碼",
        "instructions": "使用 Hotmail 帳戶密碼登入。",
    },
    "live.com": {
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "password",
        "provider_name": "Outlook (Live)",
        "auth_label": "帳戶密碼",
        "instructions": "使用 Live 帳戶密碼登入。",
    },
    "msn.com": {
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "password",
        "provider_name": "Outlook (MSN)",
        "auth_label": "帳戶密碼",
        "instructions": "使用 MSN 帳戶密碼登入。",
    },

    # --- Office 365 ---
    "office365.com": {
        "smtp_server": "smtp.office365.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "password",
        "provider_name": "Office 365",
        "auth_label": "帳戶密碼",
        "instructions": "使用 Office 365 帳戶密碼登入。若已啟用多因素驗證，請使用應用專用密碼。",
    },

    # --- NetEase Personal ---
    "163.com": {
        "smtp_server": "smtp.163.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "auth_code",
        "provider_name": "網易 163 郵箱",
        "auth_label": "授權碼",
        "instructions": "網易 163 郵箱需要授權碼，非登入密碼。請至網頁郵箱 > 設定 > POP3/SMTP/IMAP > 開啟 SMTP 服務 > 生成授權碼。",
    },
    "126.com": {
        "smtp_server": "smtp.126.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "auth_code",
        "provider_name": "網易 126 郵箱",
        "auth_label": "授權碼",
        "instructions": "網易 126 郵箱需要授權碼，非登入密碼。請至網頁郵箱 > 設定 > POP3/SMTP/IMAP > 開啟 SMTP 服務 > 生成授權碼。",
    },
    "yeah.net": {
        "smtp_server": "smtp.yeah.net",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "auth_code",
        "provider_name": "網易 Yeah 郵箱",
        "auth_label": "授權碼",
        "instructions": "網易 Yeah 郵箱需要授權碼，非登入密碼。請至網頁郵箱 > 設定 > POP3/SMTP/IMAP > 開啟 SMTP 服務 > 生成授權碼。",
    },
    "188.com": {
        "smtp_server": "smtp.188.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "auth_code",
        "provider_name": "網易 188 郵箱",
        "auth_label": "授權碼",
        "instructions": "網易 188 郵箱需要授權碼。",
    },

    # --- NetEase Enterprise / Lingxi ---
    "qiye.163.com": {
        "smtp_server": "smtphz.qiye.163.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "password_or_auth_code",
        "provider_name": "網易企業郵箱 / 靈犀",
        "auth_label": "登入密碼或授權碼",
        "instructions": "網易企業郵箱使用登入密碼。若報 ERR.LOGIN.REQCODE，請至網頁郵箱設定生成授權碼。",
    },

    # --- QQ Mail / Foxmail ---
    "qq.com": {
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "auth_code",
        "provider_name": "QQ 郵箱",
        "auth_label": "授權碼",
        "instructions": "QQ 郵箱需要授權碼，非登入密碼。請至 QQ 郵箱 > 設定 > 帳戶 > POP3/SMTP 服務 > 開啟 > 生成授權碼。",
    },
    "foxmail.com": {
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "auth_code",
        "provider_name": "Foxmail",
        "auth_label": "授權碼",
        "instructions": "Foxmail 需要授權碼（與 QQ 郵箱相同）。",
    },
    "vip.qq.com": {
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "auth_code",
        "provider_name": "QQ VIP 郵箱",
        "auth_label": "授權碼",
        "instructions": "QQ VIP 郵箱需要授權碼。",
    },

    # --- Sina ---
    "sina.com": {
        "smtp_server": "smtp.sina.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "password",
        "provider_name": "新浪郵箱",
        "auth_label": "帳戶密碼",
        "instructions": "使用新浪郵箱登入密碼。",
    },
    "sina.cn": {
        "smtp_server": "smtp.sina.cn",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "password",
        "provider_name": "新浪免費郵箱",
        "auth_label": "帳戶密碼",
        "instructions": "使用新浪郵箱登入密碼。",
    },

    # --- Sohu ---
    "sohu.com": {
        "smtp_server": "smtp.sohu.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "password",
        "provider_name": "搜狐郵箱",
        "auth_label": "帳戶密碼",
        "instructions": "使用搜狐郵箱登入密碼。",
    },

    # --- Aliyun ---
    "aliyun.com": {
        "smtp_server": "smtp.qiye.aliyun.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "password",
        "provider_name": "阿里雲郵箱",
        "auth_label": "帳戶密碼",
        "instructions": "使用阿里雲郵箱登入密碼。",
    },

    # --- Yahoo ---
    "yahoo.com": {
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "app_password",
        "provider_name": "Yahoo 郵箱",
        "auth_label": "應用專用密碼",
        "instructions": "Yahoo 郵箱需要應用專用密碼。請至 Yahoo 帳戶安全設定生成。",
    },
    "yahoo.com.tw": {
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "app_password",
        "provider_name": "Yahoo 奇摩郵箱",
        "auth_label": "應用專用密碼",
        "instructions": "Yahoo 奇摩郵箱需要應用專用密碼。",
    },
    "yahoo.com.hk": {
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "app_password",
        "provider_name": "Yahoo 香港郵箱",
        "auth_label": "應用專用密碼",
        "instructions": "Yahoo 香港郵箱需要應用專用密碼。",
    },
    "yahoo.co.jp": {
        "smtp_server": "smtp.mail.yahoo.co.jp",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "app_password",
        "provider_name": "Yahoo Japan 郵箱",
        "auth_label": "應用專用密碼",
        "instructions": "Yahoo Japan 郵箱需要應用專用密碼。",
    },

    # --- iCloud / Apple ---
    "icloud.com": {
        "smtp_server": "smtp.mail.me.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "app_password",
        "provider_name": "iCloud 郵箱",
        "auth_label": "應用專用密碼",
        "instructions": "iCloud 郵箱需要應用專用密碼。請至 Apple ID > 帳戶 > 應用專用密碼 生成。",
    },
    "me.com": {
        "smtp_server": "smtp.mail.me.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "app_password",
        "provider_name": "iCloud (Me.com)",
        "auth_label": "應用專用密碼",
        "instructions": "需要 Apple 應用專用密碼。",
    },
    "mac.com": {
        "smtp_server": "smtp.mail.me.com",
        "smtp_port": 587,
        "ssl_mode": "starttls",
        "auth_type": "app_password",
        "provider_name": "iCloud (Mac.com)",
        "auth_label": "應用專用密碼",
        "instructions": "需要 Apple 應用專用密碼。",
    },

    # --- Zoho ---
    "zoho.com": {
        "smtp_server": "smtp.zoho.com",
        "smtp_port": 465,
        "ssl_mode": "ssl",
        "auth_type": "password",
        "provider_name": "Zoho 郵箱",
        "auth_label": "帳戶密碼",
        "instructions": "使用 Zoho 郵箱登入密碼。需在 Zoho 設定中啟用 SMTP。",
    },

    # --- ProtonMail (requires Proton Bridge) ---
    "protonmail.com": {
        "smtp_server": "127.0.0.1",
        "smtp_port": 1031,
        "ssl_mode": "starttls",
        "auth_type": "password",
        "provider_name": "ProtonMail (需 Proton Bridge)",
        "auth_label": "Bridge 密碼",
        "instructions": "ProtonMail 不直接支援 SMTP。需安裝 Proton Mail Bridge 本地客戶端，並使用 Bridge 生成的密碼。",
    },
    "proton.me": {
        "smtp_server": "127.0.0.1",
        "smtp_port": 1031,
        "ssl_mode": "starttls",
        "auth_type": "password",
        "provider_name": "ProtonMail (需 Proton Bridge)",
        "auth_label": "Bridge 密碼",
        "instructions": "ProtonMail 不直接支援 SMTP。需安裝 Proton Mail Bridge 本地客戶端。",
    },

    # --- Exchange / Corporate (generic) ---
    "exchange.com": {
        "smtp_server": None,
        "smtp_port": None,
        "ssl_mode": None,
        "auth_type": "password",
        "provider_name": "Exchange (需手動設定)",
        "auth_label": "帳戶密碼",
        "instructions": "Exchange 伺服器需向 IT 管理員確認 SMTP 設定。",
    },
}


def detect_smtp_provider(email):
    """Detect SMTP provider from email domain. Returns provider info dict."""
    if "@" not in email:
        return {
            "smtp_server": None,
            "smtp_port": None,
            "ssl_mode": None,
            "auth_type": "unknown",
            "provider_name": "未知",
            "auth_label": "未知",
            "instructions": "郵箱地址格式不正確。",
            "domain": "",
            "email": email,
        }

    domain = email.split("@")[-1].lower().strip()

    # Direct match
    if domain in SMTP_PROVIDERS:
        result = dict(SMTP_PROVIDERS[domain])
        result["domain"] = domain
        result["email"] = email
        return result

    # Check for NetEase enterprise subdomains (*.qiye.163.com)
    if domain.endswith(".qiye.163.com") or domain == "qiye.163.com":
        result = dict(SMTP_PROVIDERS["qiye.163.com"])
        result["domain"] = domain
        result["email"] = email
        return result

    # Unknown domain -- enterprise or custom
    return {
        "smtp_server": None,
        "smtp_port": None,
        "ssl_mode": None,
        "auth_type": "unknown",
        "provider_name": "未知 (企業或自定義域名)",
        "auth_label": "未知",
        "instructions": "無法自動識別此郵箱提供商。請手動提供 SMTP 伺服器位址、連接埠和加密方式。常見設定：SSL 連接埠 465，STARTTLS 連接埠 587。",
        "domain": domain,
        "email": email,
    }


# ============================================================
#  Recipient parsing
# ============================================================

def parse_recipients(recipient_str):
    if not recipient_str:
        return []
    # Support comma and semicolon separators
    result = []
    for r in recipient_str.replace(";", ",").split(","):
        r = r.strip()
        if r:
            result.append(r)
    return result


# ============================================================
#  Message builder
# ============================================================

def create_message(sender_email, display_name, to_addrs, cc_addrs, bcc_addrs,
                   subject, body, is_html, attachments):
    msg = MIMEMultipart("mixed")
    if is_html:
        body_part = MIMEMultipart("alternative")
        body_part.attach(MIMEText(body, "html", "utf-8"))
        msg.attach(body_part)
    else:
        msg.attach(MIMEText(body, "plain", "utf-8"))

    from_header = f"{display_name} <{sender_email}>" if display_name else sender_email
    msg["From"] = from_header
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    msg["Subject"] = subject

    if attachments:
        for filepath in attachments:
            if not os.path.exists(filepath):
                print(f"WARNING: 附件不存在，跳過: {filepath}")
                continue
            with open(filepath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header("Content-Disposition", "attachment",
                                filename=("utf-8", "", filename))
                msg.attach(part)
            print(f"  附件已加入: {filename}")
    return msg


# ============================================================
#  SMTP connection
# ============================================================

def connect_smtp(smtp_server, smtp_port, ssl_mode, email, password):
    """Connect and login to SMTP server. Returns the server object."""
    smtp_port = int(smtp_port)

    if ssl_mode == "ssl":
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=30)
    elif ssl_mode == "starttls":
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
    else:
        # Plain (no encryption) -- not recommended
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.ehlo()

    server.login(email, password)
    return server


# ============================================================
#  Send / Preview / Test
# ============================================================

def test_connection(smtp_server, smtp_port, ssl_mode, email, password):
    """Test SMTP connection and login. Print result."""
    print("正在測試連線...")
    print(f"  伺服器: {smtp_server}:{smtp_port} ({ssl_mode.upper()})")
    print(f"  帳號: {email}")
    try:
        server = connect_smtp(smtp_server, smtp_port, ssl_mode, email, password)
        server.quit()
        print("SUCCESS: 連線成功！已取得發送郵件權限。")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: 認證失敗 -- 密碼或授權碼不正確。({e})")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"ERROR: 無法連接 SMTP 伺服器 -- 請檢查伺服器位址和連接埠。({e})")
        return False
    except smtplib.SMTPException as e:
        print(f"ERROR: SMTP 錯誤: {e}")
        return False
    except Exception as e:
        print(f"ERROR: 連線失敗: {type(e).__name__}: {e}")
        return False


def send_email(smtp_server, smtp_port, ssl_mode, email, password,
               msg, to_addrs, cc_addrs, bcc_addrs):
    """Send email via SMTP."""
    all_recipients = to_addrs + cc_addrs + bcc_addrs
    server = connect_smtp(smtp_server, smtp_port, ssl_mode, email, password)
    try:
        server.sendmail(email, all_recipients, msg.as_string())
    finally:
        server.quit()


def print_preview(sender_email, display_name, to_addrs, cc_addrs, bcc_addrs,
                  subject, body, is_html, attachments):
    """Print a human-readable preview of the email."""
    print("=" * 60)
    print("[郵件預覽]")
    if display_name:
        print(f"  寄件人:  {display_name} <{sender_email}>")
    else:
        print(f"  寄件人:  {sender_email}")
    print(f"  收件人:  {', '.join(to_addrs)}")
    if cc_addrs:
        print(f"  抄送:    {', '.join(cc_addrs)}")
    if bcc_addrs:
        print(f"  暗送:    {', '.join(bcc_addrs)}")
    print(f"  主旨:    {subject}")
    print(f"  格式:    {'HTML' if is_html else '純文字'}  ({len(body)} 字元)")
    if attachments:
        print(f"  附件:    {len(attachments)} 個")
        for a in attachments:
            print(f"           - {os.path.basename(a)}")
    else:
        print(f"  附件:    無")
    print("-" * 60)
    preview_body = body[:800]
    if len(body) > 800:
        preview_body += f"\n...[已截斷，共 {len(body)} 字元]"
    print(preview_body)
    print("=" * 60)


# ============================================================
#  Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Universal Email Sender -- runtime-only SMTP email tool"
    )

    # Mode selectors
    parser.add_argument("--detect-smtp", metavar="EMAIL",
                        help="根據郵箱地址自動偵測 SMTP 設定 (輸出 JSON)")
    parser.add_argument("--test-connection", action="store_true",
                        help="測試 SMTP 連線和認證 (不發送郵件)")
    parser.add_argument("--preview", action="store_true",
                        help="僅預覽郵件，不實際發送")

    # SMTP connection parameters (required for test/send/preview)
    parser.add_argument("--sender", "-s", help="寄件人郵箱地址")
    parser.add_argument("--smtp-server", help="SMTP 伺服器位址")
    parser.add_argument("--smtp-port", help="SMTP 連接埠")
    parser.add_argument("--ssl-mode", choices=["ssl", "starttls", "none"],
                        help="加密模式: ssl (連接埠 465) / starttls (連接埠 587) / none")
    parser.add_argument("--password", help="密碼 / 授權碼 / 應用專用密碼")
    parser.add_argument("--display-name", default="", help="寄件人顯示名稱 (選填)")

    # Email content parameters
    parser.add_argument("--to", help="收件人郵箱 (多個用逗號分隔)")
    parser.add_argument("--cc", default="", help="抄送對象 (多個用逗號分隔)")
    parser.add_argument("--bcc", default="", help="暗送對象 (多個用逗號分隔)")
    parser.add_argument("--subject", help="郵件主旨")
    parser.add_argument("--body", help="郵件內文")
    parser.add_argument("--body-file", help="從檔案讀取內文 (用於長文本或 HTML)")
    parser.add_argument("--html", action="store_true", help="標記內文為 HTML 格式")
    parser.add_argument("--attach", nargs="*", help="附件檔案路徑 (可多個)")

    args = parser.parse_args()

    # --- Mode: detect-smtp ---
    if args.detect_smtp:
        result = detect_smtp_provider(args.detect_smtp)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # --- Mode: test-connection ---
    if args.test_connection:
        if not all([args.sender, args.smtp_server, args.smtp_port,
                     args.ssl_mode, args.password]):
            print("ERROR: --test-connection 需要 --sender, --smtp-server, --smtp-port, --ssl-mode, --password")
            sys.exit(1)
        success = test_connection(args.smtp_server, args.smtp_port,
                                   args.ssl_mode, args.sender, args.password)
        sys.exit(0 if success else 1)

    # --- Mode: preview or send ---
    # Validate required parameters
    if not args.sender:
        print("ERROR: --sender 是必需的")
        sys.exit(1)
    if not args.smtp_server or not args.smtp_port or not args.ssl_mode:
        print("ERROR: --smtp-server, --smtp-port, --ssl-mode 是必需的")
        print("提示: 使用 --detect-smtp EMAIL 可自動偵測 SMTP 設定")
        sys.exit(1)
    if not args.password:
        print("ERROR: --password 是必需的 (密碼/授權碼/應用專用密碼)")
        sys.exit(1)
    if not args.to:
        print("ERROR: --to (收件人) 是必需的")
        sys.exit(1)
    if not args.subject:
        print("ERROR: --subject (郵件主旨) 是必需的")
        sys.exit(1)
    if not args.body and not args.body_file:
        print("ERROR: --body 或 --body-file 是必需的")
        sys.exit(1)

    # Parse recipients
    to_addrs = parse_recipients(args.to)
    cc_addrs = parse_recipients(args.cc)
    bcc_addrs = parse_recipients(args.bcc)

    if not to_addrs:
        print("ERROR: --to 中沒有有效的收件人地址")
        sys.exit(1)

    # Resolve body
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()
    else:
        body = args.body

    # Build message
    msg = create_message(
        args.sender,
        args.display_name,
        to_addrs, cc_addrs, bcc_addrs,
        args.subject, body, args.html,
        args.attach or [],
    )

    # Preview mode
    if args.preview:
        print_preview(args.sender, args.display_name, to_addrs, cc_addrs,
                      bcc_addrs, args.subject, body, args.html, args.attach or [])
        print("(預覽模式 -- 郵件未實際發送)")
        return

    # Send
    try:
        send_email(args.smtp_server, args.smtp_port, args.ssl_mode,
                   args.sender, args.password, msg, to_addrs, cc_addrs, bcc_addrs)
        print("SUCCESS: 郵件已成功發送！")
        print(f"  寄件人:  {args.sender}")
        print(f"  收件人:  {', '.join(to_addrs)}")
        if cc_addrs:
            print(f"  抄送:    {', '.join(cc_addrs)}")
        if bcc_addrs:
            print(f"  暗送:    {', '.join(bcc_addrs)}")
        print(f"  主旨:    {args.subject}")
        print(f"  內文:    {len(body)} 字元 ({'HTML' if args.html else '純文字'})")
        if args.attach:
            print(f"  附件:    {len(args.attach)} 個")
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: 認證失敗 -- 請檢查密碼/授權碼是否正確。({e})")
        sys.exit(1)
    except smtplib.SMTPConnectError as e:
        print(f"ERROR: 無法連接 SMTP 伺服器 -- 請檢查伺服器位址和連接埠。({e})")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(f"ERROR: SMTP 錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: 發送失敗: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
