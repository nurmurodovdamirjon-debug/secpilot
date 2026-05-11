# Honeypot & Canary Design

## 1. Maqsad

Honeypot/canary attackerga hujum qilmaydi. U faqat attacker sizning tizimingizga tegsa, iz qoldirishini ta’minlaydi.

## 2. Honeypot endpointlar

```text
/admin-old
/.env
/phpmyadmin
/wp-login.php
/backup.zip
/config.php
/debug
/console-login
```

## 3. Loglanadigan ma’lumotlar

- IP
- vaqt
- endpoint
- HTTP method
- user-agent
- headers hash/summary
- payload preview
- ASN
- provider
- country
- TOR/VPN ehtimoli
- risk score

## 4. Canary tokenlar

Turlar:

- URL canary
- fake API key
- fake `.env` entry
- fake backup file
- DNS canary

## 5. Alert namunasi

```text
🍯 Honeypot Triggered

Endpoint: /.env
IP: 185.xxx.xxx.xxx
ASN: AS24940
Provider: Hetzner
User-Agent: curl/7.81.0
Risk: HIGH

Action:
✅ Evidence saved
✅ Temporary block suggested
```

## 6. Qoidalar

- real credential qo‘yilmaydi
- attackerga zararli fayl berilmaydi
- malware yuborilmaydi
- faqat metadata yig‘iladi
- false positive ehtimoli hisobga olinadi
