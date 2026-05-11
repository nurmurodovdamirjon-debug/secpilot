# ADR-0002: Go Scanner Service

## Status

Proposed

## Context

Port va network scan ko‘p parallel socket ishlarini talab qiladi.

## Decision

Yuklama oshganda port/network scanner Go microservicega ajratiladi.

## Trigger

- p95 scan time > 10s
- queue depth > 100
- Python worker CPU/socket pressure yuqori
- bir vaqtda ko‘p host tekshiriladi

## API

`POST /internal/scanner/port-scan`

## Guardrail

- faqat whitelist target
- private range deny unless explicit scope
- rate limit
- audit log
