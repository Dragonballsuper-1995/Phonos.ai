---
title: Phonos AI API
emoji: 📱
colorFrom: purple
colorTo: blue
sdk: docker
pinned: true
app_port: 7860
---

# Phonos.ai — Backend API

FastAPI backend powering the **Phonos.ai** smartphone recommendation engine for the Indian market.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check + DB status |
| GET | `/api/v1/phones` | List all phones |
| POST | `/api/v1/recommend/easy` | Easy persona-based recommendation |
| POST | `/api/v1/recommend/medium` | Medium mode with priority weights |
| GET | `/api/v1/phones/search?q=` | Search phones by name/brand |

## Tech Stack

- **FastAPI** with async SQLite (`aiosqlite`)
- **Embedded database**: `fone_master.db` (~49 MB, included in the Docker image)
- **Scoring engine**: Persona-weighted match scoring with age multipliers
