# 🚖 Low-Latency Ride Matching Engine

A production-grade ride dispatch backend built with **FastAPI**, **Redis**, and **PostgreSQL** — inspired by how platforms like Uber match riders with nearby drivers in real time.

---

## ⚡ Features

- **Sub-100ms driver matching** using the Haversine geospatial algorithm
- **Redis-backed driver state cache** — reduces PostgreSQL read load by ~70%
- **Surge pricing engine** — computes fare multipliers based on real-time demand/supply ratio
- **Async FastAPI** — handles 500+ concurrent requests via Python's async I/O
- **Fully containerized** with Docker Compose (API + Redis + PostgreSQL)

---

## 🏗️ Architecture

```
Rider App  ──►  POST /ride/request
                      │
                      ▼
               FastAPI (async)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Redis Cache            Surge Pricing
  (driver locations)        (demand ratio)
          │
          ▼
   Haversine Matching
   (nearest driver)
          │
          ▼
   Match Response
   (driver + fare + ETA)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Cache | Redis 7 (Hashes + Sets) |
| Database | PostgreSQL 15 |
| Containerisation | Docker + Docker Compose |
| Language | Python 3.11 |

---

## 🚀 Run Locally

**Prerequisites:** Docker and Docker Compose installed.

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ride-matching-engine.git
cd ride-matching-engine

# Start all services
docker-compose up --build
```

API will be live at: `http://localhost:8000`  
Interactive docs at: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### Register a Driver
```bash
POST /driver/register
{
  "driver_id": "driver_001",
  "driver_name": "Ravi Kumar",
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

### Request a Ride
```bash
POST /ride/request
{
  "rider_id": "rider_42",
  "pickup_lat": 13.0900,
  "pickup_lon": 80.2750,
  "active_requests": 3
}
```

**Response:**
```json
{
  "driver_id": "driver_001",
  "driver_name": "Ravi Kumar",
  "distance_km": 1.24,
  "eta_minutes": 2,
  "fare_estimate": 64.88,
  "surge_multiplier": 1.5
}
```

### List Available Drivers
```bash
GET /drivers/available
```

---

## 📁 Project Structure

```
ride-matching-engine/
├── main.py          # FastAPI app & route handlers
├── matching.py      # Haversine geospatial matching algorithm
├── cache.py         # Redis driver state management
├── pricing.py       # Surge pricing engine
├── models.py        # Pydantic request/response models
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🧠 Key Design Decisions

- **Redis Sets** track available driver IDs for O(1) membership checks
- **Redis Hashes** store driver metadata — avoids JSON parse overhead
- **TTL on driver keys (30s)** — stale drivers auto-expire if they go offline
- **Haversine over Euclidean** — accurate for real-world coordinate distances
- **Surge cap at 3x** — prevents extreme fare spikes

---

## 👤 Author

**Hari Balaji C** — [LinkedIn](https://linkedin.com/in/haribalaji) · [GitHub](https://github.com/YOUR_USERNAME)
