# 🚀 Building Agents with Redis Caching and Observability

This project demonstrates how to build intelligent, LLM-powered agents that interact with databases using **natural language queries**. It leverages **Redis** for both **caching** and **real-time PUB/SUB communication**, and integrates full observability using **Grafana, Prometheus, Loki**, and **Promtail**.

---

## 📦 Features

* 🔍 **Natural Language to SQL**: Translate user input into SQL queries using **Google Gemini** LLM
* 🗂️ **SQLite Integration**: Execute SQL queries on a local SQLite database
* 🧠 **LLM Summarization**: Generate human-readable summaries of the query results
* ⚡ **Redis Caching**: Store results of frequently used queries to minimize repeated LLM calls
* 🔄 **Redis PUB/SUB**: Enable communication between microservices or agent modules
* 📈 **Monitoring & Logging**: Full observability stack with **Prometheus**, **Grafana**, **Loki**, and **Promtail**

---

## 🛠️ Tech Stack

* **Python 3.10+**
* **Redis** (`redis-py`)
* **SQLite** (for lightweight data storage)
* **Pandas** (for CSV ingestion)
* **Google Generative AI SDK** (`google.generativeai`)
* **Gemini LLM** (Google’s large language model for SQL generation and summaries)
* **Grafana** (for dashboards and alerts)
* **Prometheus** (for metrics collection)
* **Loki + Promtail** (for log aggregation)

---




---

## 📊 Monitoring & Observability

### 🔍 Metrics with Prometheus + Grafana

* API response times
* Redis cache hit/miss ratio
* LLM query latency
* Request count per endpoint

### 📋 Logs with Loki + Promtail

* Centralized logging for all containers
* Real-time log search through Grafana interface
* Error tracebacks and request logs

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/TanmayAT/redis.git

cd redis
```

### 2. Start the Project

Use Docker Compose to spin up Redis, Prometheus, Loki, and Grafana:

```bash
docker-compose up --build
```

```bash
docker ps

```

```bash

docker logs <container-id>

```

If you want watch logs 

```bash
docker-compose build

```

```bash
docker-compose up

```


]

## 📬 TODOs / Roadmap

* [ ] Add authentication and rate limiting
* [ ] Add support for multiple databases
* [ ] Enhance agent reasoning with memory and feedback loops

---