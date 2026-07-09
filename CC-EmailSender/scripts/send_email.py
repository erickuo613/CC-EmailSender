#!/usr/bin/env python3
"""
Email Sender — multi-profile SMTP email tool.

Supports:
  - Multiple sender profiles (add, list, select)
  - Password memory per account (stored separately)
  - Contacts management per sender (manual, persistent)
  - Preview before sending (--preview)
  - Plain text and HTML body
  - Multiple recipients (To, CC, BCC)
  - File attachments
  - Unicode subject and body (UTF-8)

"""

import sys
import io

# Fix Windows console encoding for Chinese characters
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse
import json
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- Paths ---
CONFIG_DIR = os.path.join(
    os.path.expanduser("~"), ".workbuddy", "skills", "CC-EmailSender", "config"
)
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "email_config.json")
PASSWORD_STORE_PATH = os.path.join(CONFIG_DIR, "passwords.json")
CONTACTS_PATH = os.path.join(CONFIG_DIR, "contacts.json")


# ============================================================
#  Config / Profile management
# ============================================================

def load_profiles(config_path=None):
    """Load the multi-profile config.  Returns the full JSON dict."""
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found at: {config_path}")
        print("Run with --init-config to create one.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Support legacy single-account format → migrate on the fly
    if "profiles" not in config:
        if "username" in config:
            config["profiles"] = [{
                "email": config["username"],
                "display_name": config.get("display_name", ""),
                "smtp_server": config["smtp_server"],
                "smtp_port": config["smtp_port"],
                "use_ssl": config.get("use_ssl", True),
            }]
        else:
            print("ERROR: Config file has no 'profiles' array and is not a legacy single-account format.")
            sys.exit(1)

    return config


def save_profiles(config, config_path=None):
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def find_profile(config, email):
    """Return (profile_dict, index) or (None, -1)."""
    for i, p in enumerate(config.get("profiles", [])):
        if p.get("email") == email:
            return p, i
    return None, -1


def list_profiles_action(config_path=None):
    """Print all profiles as JSON to stdout (for assistant consumption)."""
    config = load_profiles(config_path)
    profiles = config.get("profiles", [])
    # Output clean summary for both human and machine reading
    result = []
    for p in profiles:
        result.append({
            "email": p["email"],
            "display_name": p.get("display_name", ""),
            "smtp_server": p.get("smtp_server", ""),
        })
    print(json.dumps(result, indent=2, ensure_ascii=False))


def add_profile_action(config_path=None):
    """Interactive flow to add a new sender profile."""
    config = load_profiles(config_path)
    print("=== 新增寄件人 ===")
    email = input("Email 地址: ").strip()
    if not email:
        print("ERROR: Email 地址不能为空")
        sys.exit(1)
    existing, _ = find_profile(config, email)
    if existing:
        print(f"WARNING: {email} 已存在。将会覆盖。")
    display_name = input("显示名称 (留空跳过): ").strip()
    smtp_server = input("SMTP 服务器 [smtphz.qiye.163.com]: ").strip() or "smtphz.qiye.163.com"
    smtp_port = input("SMTP 端口 [465]: ").strip() or "465"
    use_ssl = input("使用 SSL? (Y/n): ").strip().lower() != "n"

    profile = {
        "email": email,
        "display_name": display_name,
        "smtp_server": smtp_server,
        "smtp_port": int(smtp_port),
        "use_ssl": use_ssl,
    }

    if existing:
        config["profiles"][_] = profile
    else:
        config["profiles"].append(profile)

    save_profiles(config, config_path)

    # Ask if user wants to save password
    save_pwd = input("是否一并保存密码? (y/N): ").strip().lower()
    if save_pwd == "y":
        password = input("密码/授权码: ").strip()
        save_password(email, password)
        print(f"密码已保存 for {email}")
    print(f"Profile '{email}' 已新增。")


# ============================================================
#  Password store (separate file)
# ============================================================

def load_passwords():
    if not os.path.exists(PASSWORD_STORE_PATH):
        return {}
    with open(PASSWORD_STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_password(email, password):
    pwds = load_passwords()
    pwds[email] = password
    os.makedirs(os.path.dirname(PASSWORD_STORE_PATH), exist_ok=True)
    with open(PASSWORD_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(pwds, f, indent=2, ensure_ascii=False)


def get_password(email):
    """Return saved password or None."""
    pwds = load_passwords()
    return pwds.get(email)


# ============================================================
#  Contacts management (per sender, manually maintained)
# ============================================================

def load_contacts():
    """Load contacts store. Returns dict keyed by sender email, each with a list of {name, email}."""
    if not os.path.exists(CONTACTS_PATH):
        return {}
    try:
        with open(CONTACTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_contacts(data):
    os.makedirs(os.path.dirname(CONTACTS_PATH), exist_ok=True)
    with open(CONTACTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_contacts(sender_email):
    """Return contact list for a sender. List of {name, email}."""
    data = load_contacts()
    return data.get(sender_email, [])


def add_contact_action(sender_email=None):
    """Interactive flow to add a contact. If sender_email is given, add to that sender only."""
    data = load_contacts()

    if sender_email:
        # Specific sender
        name = input("联系人姓名: ").strip()
        email = input("联系人邮箱: ").strip()
        if not name or not email:
            print("ERROR: 姓名和邮箱不能为空")
            sys.exit(1)
        if sender_email not in data:
            data[sender_email] = []
        # Avoid duplicates
        existing = [c for c in data[sender_email] if c["email"] == email]
        if existing:
            print(f"WARNING: {email} 已存在，将更新姓名。")
            existing[0]["name"] = name
        else:
            data[sender_email].append({"name": name, "email": email})
        print(f"联系人 '{name}' <{email}> 已添加。")
    else:
        # Global: ask which sender
        config = load_profiles()
        profiles = config.get("profiles", [])
        if not profiles:
            print("ERROR: 没有已配置的寄件人。请先 --add-profile。")
            sys.exit(1)

        print("=== 新增联系人 ===")
        print("选择归属的寄件人账户:")
        for i, p in enumerate(profiles):
            print(f"  {i+1}. {p['email']}")
        try:
            idx = int(input("请输入序号: ").strip()) - 1
            sender_email = profiles[idx]["email"]
        except (ValueError, IndexError):
            print("ERROR: 无效的序号")
            sys.exit(1)

        name = input("联系人姓名: ").strip()
        email = input("联系人邮箱: ").strip()
        if not name or not email:
            print("ERROR: 姓名和邮箱不能为空")
            sys.exit(1)
        if sender_email not in data:
            data[sender_email] = []
        existing = [c for c in data[sender_email] if c["email"] == email]
        if existing:
            print(f"WARNING: {email} 已存在，将更新姓名。")
            existing[0]["name"] = name
        else:
            data[sender_email].append({"name": name, "email": email})
        print(f"联系人 '{name}' <{email}> 已添加到 {sender_email}。")

    save_contacts(data)


def list_contacts_action(sender_email):
    """Print contacts for a sender as JSON."""
    contacts = get_contacts(sender_email)
    print(json.dumps(contacts, indent=2, ensure_ascii=False))


# ============================================================
#  Recipient parsing
# ============================================================

def parse_recipients(recipient_str):
    if not recipient_str:
        return []
    return [r.strip() for r in recipient_str.split(",") if r.strip()]


# ============================================================
#  Message builder
# ============================================================

def create_message(sender_email, display_name, to_addrs, cc_addrs, subject, body, is_html, attachments):
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
                print(f"WARNING: 附件不存在，跳过: {filepath}")
                continue
            with open(filepath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", filename))
                msg.attach(part)
            print(f"  附件: {filename}")
    return msg


# ============================================================
#  Send / Preview
# ============================================================

def send_email(profile, password, msg, to_addrs, cc_addrs, bcc_addrs):
    smtp_server = profile["smtp_server"]
    smtp_port = int(profile["smtp_port"])
    use_ssl = profile.get("use_ssl", True)
    all_recipients = to_addrs + cc_addrs + bcc_addrs

    if use_ssl:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=30) as server:
            server.login(profile["email"], password)
            server.sendmail(profile["email"], all_recipients, msg.as_string())
    else:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(profile["email"], password)
            server.sendmail(profile["email"], all_recipients, msg.as_string())


def print_preview(profile, to_addrs, cc_addrs, bcc_addrs, subject, body, is_html, attachments):
    """Print a human-readable preview of the email."""
    display = profile.get("display_name", "")
    print("=" * 50)
    print("【邮件预览】")
    print(f"  发件人: {display} <{profile['email']}>" if display else f"  发件人: {profile['email']}")
    print(f"  收件人: {', '.join(to_addrs)}")
    if cc_addrs:
        print(f"  抄送:   {', '.join(cc_addrs)}")
    if bcc_addrs:
        print(f"  密送:   {', '.join(bcc_addrs)}")
    print(f"  主旨:   {subject}")
    print(f"  格式:   {'HTML' if is_html else '纯文本'}  ({len(body)} 字符)")
    if attachments:
        print(f"  附件:   {len(attachments)} 个")
        for a in attachments:
            print(f"          - {os.path.basename(a)}")
    print("-" * 50)
    # Show first 500 chars of body
    preview_body = body[:500]
    if len(body) > 500:
        preview_body += "\n...[截断，共 {} 字符]".format(len(body))
    print(preview_body)
    print("=" * 50)


# ============================================================
#  Init config
# ============================================================

def init_config(config_path):
    template = {
        "profiles": []
    }
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    if os.path.exists(config_path):
        overwrite = input(f"Config 已存在: {config_path}\n覆盖? (y/N): ").strip().lower()
        if overwrite != "y":
            print("已取消。")
            return
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"Config 已创建: {config_path}")
    print("请用 --add-profile 新增寄件人，或手动编辑 profiles 数组。")


# ============================================================
#  Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Email Sender — multi-profile SMTP tool")

    # Profile / config management
    parser.add_argument("--init-config", action="store_true", help="创建空的 profiles 配置文件")
    parser.add_argument("--add-profile", action="store_true", help="交互式新增寄件人")
    parser.add_argument("--list-profiles", action="store_true", help="列出所有已配置的寄件人 (JSON)")
    parser.add_argument("--add-contact", action="store_true", help="交互式新增联系人（可配合 --sender 指定归属账户）")
    parser.add_argument("--list-contacts", metavar="SENDER_EMAIL", help="列出某寄件人的所有联系人 (JSON)")
    parser.add_argument("--config", default=None, help="配置文件路径 (默认: ~/.workbuddy/skills/CC-EmailSender/config/email_config.json)")

    # Sender selection
    parser.add_argument("--sender", "-s", help="选择寄件人邮箱 (必须存在于 profiles 中)")

    # Email parameters
    parser.add_argument("--to", help="收件人，多个用逗号分隔")
    parser.add_argument("--cc", default="", help="抄送，多个用逗号分隔")
    parser.add_argument("--bcc", default="", help="密送，多个用逗号分隔")
    parser.add_argument("--subject", help="邮件主旨")
    parser.add_argument("--body", help="邮件正文")
    parser.add_argument("--body-file", help="从文件读取正文 (用于长文本或HTML)")
    parser.add_argument("--html", action="store_true", help="正文为 HTML 格式")
    parser.add_argument("--attach", nargs="*", help="附件文件路径")
    parser.add_argument("--password", help="密码/授权码。留空则自动从密码存储中读取。填写 'ask' 表示运行时由用户输入。")

    # Preview mode
    parser.add_argument("--preview", action="store_true", help="仅预览，不实际发送")

    args = parser.parse_args()

    # --- Management actions ---
    if args.init_config:
        init_config(args.config or DEFAULT_CONFIG_PATH)
        return

    if args.add_profile:
        add_profile_action(args.config or DEFAULT_CONFIG_PATH)
        return

    if args.list_profiles:
        list_profiles_action(args.config or DEFAULT_CONFIG_PATH)
        return

    if args.add_contact:
        add_contact_action(sender_email=args.sender)
        return

    if args.list_contacts:
        list_contacts_action(args.list_contacts)
        return

    # --- Validate sending args ---
    if not args.sender:
        print("ERROR: --sender 是必需的 (用 --list-profiles 查看已配置的寄件人)")
        sys.exit(1)
    if not args.to:
        print("ERROR: --to 是必需的")
        sys.exit(1)
    if not args.subject:
        print("ERROR: --subject 是必需的")
        sys.exit(1)
    if not args.body and not args.body_file:
        print("ERROR: --body 或 --body-file 是必需的")
        sys.exit(1)

    # --- Load profile ---
    config = load_profiles(args.config)
    profile, _ = find_profile(config, args.sender)
    if not profile:
        avail = [p["email"] for p in config.get("profiles", [])]
        print(f"ERROR: 找不到寄件人 '{args.sender}'")
        if avail:
            print(f"可用寄件人: {', '.join(avail)}")
        else:
            print("尚未配置任何寄件人。请先用 --add-profile 新增。")
        sys.exit(1)

    # --- Resolve password ---
    password = args.password
    if not password:
        password = get_password(args.sender)
        if not password:
            print(f"ERROR: 未找到 {args.sender} 的密码。请用 --password 提供，或先执行 --add-profile 并保存密码。")
            sys.exit(1)
    elif password.lower() == "ask":
        import getpass
        password = getpass.getpass(f"请输入 {args.sender} 的密码/授权码: ").strip()
        if not password:
            print("ERROR: 密码不能为空")
            sys.exit(1)

    # --- Parse recipients ---
    to_addrs = parse_recipients(args.to)
    cc_addrs = parse_recipients(args.cc)
    bcc_addrs = parse_recipients(args.bcc)

    if not to_addrs:
        print("ERROR: --to 中没有有效的收件人")
        sys.exit(1)

    # --- Body ---
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()
    else:
        body = args.body

    # --- Build message ---
    msg = create_message(
        profile["email"],
        profile.get("display_name", ""),
        to_addrs, cc_addrs,
        args.subject, body, args.html, args.attach,
    )

    # --- Preview mode ---
    if args.preview:
        print_preview(profile, to_addrs, cc_addrs, bcc_addrs, args.subject, body, args.html, args.attach)
        print("(预览模式 — 邮件未实际发送)")
        return

    # --- Send ---
    try:
        send_email(profile, password, msg, to_addrs, cc_addrs, bcc_addrs)
        print(f"SUCCESS: 邮件已发送!")
        print(f"  发件人: {profile['email']}")
        print(f"  收件人: {', '.join(to_addrs)}")
        if cc_addrs:
            print(f"  抄送:   {', '.join(cc_addrs)}")
        if bcc_addrs:
            print(f"  密送:   {', '.join(bcc_addrs)}")
        print(f"  主旨:   {args.subject}")
        print(f"  正文:   {len(body)} 字符 ({'HTML' if args.html else '纯文本'})")
        if args.attach:
            print(f"  附件:   {len(args.attach)} 个")
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: 认证失败，请检查密码/授权码。({e})")
        sys.exit(1)
    except smtplib.SMTPConnectError as e:
        print(f"ERROR: 无法连接 SMTP 服务器，请检查服务器地址和端口。({e})")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(f"ERROR: SMTP 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: 发送失败: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
