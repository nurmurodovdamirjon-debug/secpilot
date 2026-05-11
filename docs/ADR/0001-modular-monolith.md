# ADR-0001: Modular Monolith bilan boshlash

## Status

Accepted

## Context

Loyiha boshida kichik jamoa yoki bitta developer tomonidan ishlab chiqiladi. Microservice boshidan ishlatilsa, deploy, monitoring, debugging va contract management murakkablashadi.

## Decision

Boshlanishda Python modular monolith ishlatiladi:

- aiogram bot
- FastAPI core
- workers
- services modullari
- PostgreSQL
- Redis

## Consequences

Yaxshi:
- tez development
- oson deploy
- kam operational xarajat
- keyin extraction oson

Yomon:
- katta yuklamada ayrim modullar ajratilishi kerak

## Extraction trigger

- port scanning og‘irlashsa → Go
- file/static analysis og‘irlashsa → Rust
