# Security Policy

## 1. Asosiy tamoyillar

- Faqat ruxsatli targetlar
- Least privilege
- Human-in-the-loop
- Reversible defense
- Audit log hamma joyda
- Secretlar himoyalangan
- AI tool access cheklangan

## 2. Taqiqlangan funksiyalar

SecPilot quyidagilarni bajarmaydi:

- hack-back
- malware yaratish
- phishing kit yaratish
- account buzish
- credential theft
- exploit delivery
- ruxsatsiz scanning
- persistence yoki evasion

## 3. Ruxsat etilgan funksiyalar

- Defensive monitoring
- Authorized audit
- Honeypot/canary
- IP reputation
- Cloudflare WAF/rate-limit
- UFW/Fail2Ban block
- Incident report
- Security hardening recommendation

## 4. Approval matrix

| Action | Auto | Manual approval |
|---|---|---|
| Read server metrics | ✅ | ❌ |
| SSL/header/DNS audit | ✅ | ❌ |
| Honeypot event log | ✅ | ❌ |
| Single IP temporary block | ✅, high confidence | Tavsiya |
| ASN block | ❌ | ✅ |
| Country block | ❌ | ✅ |
| Cloudflare Under Attack global | ❌ | ✅ |
| Service restart | ❌ | ✅ |
| Secret rotation | ❌ | ✅ |

## 5. Secret handling

- `.env` faqat local dev
- productionda secret manager tavsiya qilinadi
- tokenlar logga chiqmaydi
- tokenlar mask qilinadi
- token rotation hujjatlashtiriladi

## 6. Audit log

Har action:

- kim bajardi
- qachon bajardi
- qaysi target
- natija
- request_id
- correlation_id

bilan yoziladi.

## 7. Safe failure

- scope noaniq bo‘lsa: deny
- AI ishonchi past bo‘lsa: propose only
- Cloudflare API fail bo‘lsa: retry storm qilinmaydi
- DB down bo‘lsa: yangi risky action bajarilmaydi
