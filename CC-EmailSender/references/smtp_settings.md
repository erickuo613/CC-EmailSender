# SMTP Server Settings Reference

Common email providers and their SMTP settings for quick lookup.

## NetEase Enterprise / Lingxi (网易企业邮箱 / 灵犀)

| Protocol | Server | SSL Port | Non-SSL Port |
|----------|--------|----------|--------------|
| SMTP (send) | smtphz.qiye.163.com | 465 / 994 / 587 | 25 |
| POP3 (receive) | pophz.qiye.163.com | 995 | 110 |
| IMAP (receive) | imaphz.qiye.163.com | 993 | 143 |

> Note: `hz` = East China (华东) region. For North China (华北), the server may use a different prefix.
> Always use SSL encryption (recommended by NetEase).
> Some enterprise deployments may require an authorization code (授权码) instead of the login password.
> If you get `535 ERR.LOGIN.REQCODE`, go to webmail Settings → Client Settings → enable SMTP and generate an auth code.

## NetEase Personal Email (163 / 126 / yeah.net)

| Domain | SMTP Server | SSL Port | Non-SSL Port |
|--------|------------|----------|--------------|
| 163.com | smtp.163.com | 465 / 994 | 25 |
| 126.com | smtp.126.com | 465 / 994 | 25 |
| yeah.net | smtp.yeah.net | 465 / 994 | 25 |
| 188.com | smtp.188.com | 465 / 994 | 25 |
| netease.com | smtp.netease.com | 465 / 994 | 25 |

> Personal NetEase email requires an authorization code (授权码), NOT the login password.
> Enable IMAP/SMTP service in webmail settings first, then generate the auth code.

## Gmail

| Protocol | Server | SSL Port | TLS Port |
|----------|--------|----------|----------|
| SMTP | smtp.gmail.com | 465 | 587 |

> Requires App Password (2FA must be enabled). Regular password will NOT work.

## Outlook / Office365

| Protocol | Server | SSL Port | TLS Port |
|----------|--------|----------|----------|
| SMTP | smtp-mail.outlook.com | - | 587 |
| SMTP (O365) | smtp.office365.com | - | 587 |

## QQ Mail

| Protocol | Server | SSL Port |
|----------|--------|----------|
| SMTP | smtp.qq.com | 465 |

> Requires authorization code (授权码), NOT the login password.

## Authentication Notes

- **NetEase Enterprise**: Use the email login password directly (no auth code needed).
- **NetEase Personal**: Enable IMAP/SMTP in webmail settings, then use the generated auth code.
- **Gmail**: Enable 2FA, then create an App Password at Google Account settings.
- **QQ Mail**: Enable IMAP/SMTP service, then use the generated auth code.
