# Deployment Guide

## 1. Local development

```bash
cp .env.example .env
docker compose up --build
```

## 2. Minimal production

- Ubuntu VPS
- Docker Compose
- Nginx reverse proxy
- Cloudflare DNS/WAF
- PostgreSQL
- Redis
- Telegram bot token
- nightly backup

## 3. Services

```text
api
bot
worker
postgres
redis
```

## 4. Health checks

- `/health/live`
- `/health/ready`
- worker heartbeat
- Redis ping
- PostgreSQL connection
- Telegram bot auth

## 5. Production checklist

- [ ] `.env` to‘ldirilgan
- [ ] BOT_ADMIN_IDS to‘g‘ri
- [ ] DB password kuchli
- [ ] Cloudflare token scoped
- [ ] backup script ishlaydi
- [ ] restore test qilingan
- [ ] firewall faqat kerakli portlarni ochgan
- [ ] logs rotation yoqilgan
- [ ] monitoring alerts yoqilgan

## 6. Rollback

1. risky automation pause
2. previous Docker image tagga qaytish
3. DB migration compatibility tekshirish
4. smoke test
5. incident log yozish
