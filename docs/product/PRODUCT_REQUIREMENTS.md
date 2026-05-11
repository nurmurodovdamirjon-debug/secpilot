# Product Requirements Document — SecPilot Defense

## 1. Loyiha tavsifi

SecPilot Defense — bu Telegram-first shaxsiy cybersecurity assistant. U foydalanuvchining ruxsat berilgan infratuzilmasida monitoring, audit, hujumlarni aniqlash, deception, dalil yig‘ish va himoya avtomatizatsiyasini bajaradi.

## 2. Muammo

Kichik jamoalar va yakka developerlar server, bot, API va web loyihalariga bo‘layotgan hujumlarni vaqtida sezmaydi. Loglar tarqoq, alertlar yo‘q, Cloudflare/firewall response qo‘lda, incident report esa keyin yoziladi.

## 3. Yechim

Telegram ichida ishlaydigan boshqaruv paneli:

- server holatini ko‘rsatadi
- hujumlarni aniqlaydi
- attacker infrastructure haqida ma’lumot yig‘adi
- honeypot va canary orqali iz qoldirtiradi
- xavfsiz defense action bajaradi
- AI bilan tushuntiradi
- hisobot yaratadi

## 4. Asosiy foydalanuvchi

- Owner: bitta asosiy Telegram ID
- Admin: keyingi bosqichda
- Read-only: keyingi bosqichda

## 5. MVP scope

### Kiritiladi

1. Telegram owner whitelist
2. Target whitelist
3. Server status monitor
4. SSL/DNS/Header audit
5. Log analyzer
6. Honeypot endpointlar
7. Canary token
8. IP reputation
9. Auto alert
10. Manual-approved IP block
11. Incident report
12. AI triage summary

### Kiritilmaydi

1. Public SaaS multi-tenant billing
2. Real exploit execution
3. Malware analysis sandbox dynamic execution
4. Hack-back
5. Ruxsatsiz scanning

## 6. Success metrics

- Critical alert Telegramga 60 soniya ichida yetib boradi
- False auto-block < 1%
- Server health check har 1–5 daqiqada
- Incident report 1 daqiqa ichida generatsiya bo‘ladi
- Target whitelist bypass mumkin emas

## 7. Telegram commandlar

```text
/start
/help
/status
/servers
/add_target
/my_targets
/check_web
/check_ssl
/check_dns
/check_ports
/honeypot
/canary
/alerts
/incidents
/block_ip
/unblock_ip
/report
/ai
/settings
```

## 8. Asosiy ekran/menyu

```text
🏠 Bosh menyu
├ 🖥 Server Monitoring
├ 🚨 Attack Detection
├ 🍯 Deception Engine
├ 🌐 Web Audit
├ 🛡 Defense Actions
├ 🤖 AI Assistant
├ 📊 Reports
└ ⚙️ Settings
```
