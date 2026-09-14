# VoxCPM2 TTS + FastAPI 

VoxCPM is a text-to-speech (TTS) FastAPI service that generates spoken audio in Khmer (and other supported languages), including special support for reading out transaction amounts (e.g. payment confirmations).

## Table of Contents

- [Requirements](#requirements)
- [Running the App](#running-the-app)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [1. Generate Transaction Voice](#1-generate-transaction-voice)
  - [2. Generate Voice](#2-generate-voice)
  - [3. Health Check](#3-health-check)

---

## Requirements

- Python 3+ (This project running on version 3.10.10)
- FastAPI
- Uvicorn (ASGI server)
- Any additional dependencies listed in `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

Assuming your FastAPI entrypoint is `main.py` with an app instance named `app`:

```bash
uvicorn app:app --reload
```

For production, drop `--reload` and consider running behind a process manager (e.g. `gunicorn` with `uvicorn.workers.UvicornWorker`, or a container/orchestrator).

Once running, the API will be available at:

```
http://127.0.0.1:8000
```

---

## Base URL

```
http://127.0.0.1:8000
```

---

## Endpoints

### 1. Generate Transaction Voice

Generates spoken audio announcing a transaction amount (e.g. for payment confirmation playback).

- **Method:** `POST`
- **URL:** `/openai/api/v1/speech/generate`
- **Auth:** None

**Request Body** (`application/json`):

```json
{
  "language": "km-kh",
  "currency": "USD",
  "voice": "piseth",
  "amount": "10.89"
}
```

| Field      | Type   | Description                                                      |
|------------|--------|----------------------------------------------------------        |
| `language` | string | Language/locale code for speech synthesis (e.g. `km-kh`)         |
| `currency` | string | Currency code for the amount (e.g. `USD`, `KHR`)                 |
| `voice`    | string | Voice preset/name to use for synthesis (e.g. `piseth`,`sreymom`) |
| `amount`   | string | Transaction amount to be spoken aloud                            |

**Example cURL:**

```bash
curl -X POST http://127.0.0.1:8000/openai/api/v1/speech/generate \
  -H "Content-Type: application/json" \
  -d '{
    "language": "km-kh",
    "currency": "USD",
    "voice": "piseth",
    "amount": "10.89"
  }'
```

---

### 2. Generate Voice

Generates spoken audio from arbitrary free-form text content.

- **Method:** `POST`
- **URL:** `/openai/api/v1/speech/speak`
- **Auth:** None

**Request Body** (`application/json`):

```json
{
  "language": "km-kh",
  "currency": "KHR",
  "voice": "sreymom",
  "content": "ទទួលបាន ការបញ្ចុះតម្លៃរហូតដល់ 15% លើមុខម្ហូបនៅភោជនីយដ្ឋានដៃគូជាច្រើន ដោយគ្រាន់តែទូទាត់តាមរយៈកាត Visa របស់ធនាគារ ជីប ម៉ុង។"
}
```

| Field      | Type   | Description                                                      |
|------------|--------|----------------------------------------------------------        |
| `language` | string | Language/locale code for speech synthesis (e.g. `km-kh`)         |
| `voice`    | string | Voice preset/name to use for synthesis (e.g. `piseth`,`sreymom`) |
| `amount`   | string | Transaction amount to be spoken aloud                            |

**Example cURL:**

```bash
curl -X POST http://127.0.0.1:8000/openai/api/v1/speech/speak \
  -H "Content-Type: application/json" \
  -d '{
    "language": "km-kh",
    "voice": "sreymom",
    "content": "ទទួលបាន ការបញ្ចុះតម្លៃរហូតដល់ 15% លើមុខម្ហូបនៅភោជនីយដ្ឋានដៃគូជាច្រើន ដោយគ្រាន់តែទូទាត់តាមរយៈកាត Visa របស់ធនាគារ ជីប ម៉ុង។"
  }'
```

---

### 3. Health Check

Checks whether the API service is up and running.

- **Method:** `GET`
- **URL:** `/health`
- **Auth:** None

**Example cURL:**

```bash
curl http://127.0.0.1:8000/health
```

**Example Response:**

```json
{
  "status": "ok"
}
```

*(Actual response shape depends on your implementation.)*

---

## Notes

- All endpoints currently require **no authentication** (`noauth`), so this setup is suitable for local development only. Add authentication (API key, OAuth, etc.) before deploying publicly.