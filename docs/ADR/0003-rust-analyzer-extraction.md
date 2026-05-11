# ADR-0003: Rust Analyzer Service

## Status

Proposed

## Context

File/APK/static analysis CPU-heavy bo‘lishi mumkin.

## Decision

Yuklama oshsa analyzer Rust servicega ajratiladi.

## Trigger

- CPU > 80%
- katta fayllar sekin tahlil qilinadi
- entropy/string extraction og‘ir
- memory safety muhim

## API

`POST /internal/analyzer/file`

## Guardrail

- fayl execute qilinmaydi
- faqat static analysis
- quarantine path
- hash validation
