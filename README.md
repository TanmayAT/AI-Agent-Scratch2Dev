# 🚀 Building Agents with Redis Caching

This project demonstrates how to build intelligent agents that interact with databases using natural language queries, powered by LLMs (e.g., Gemini), with Redis used for **caching** and **PUB/SUB communication** to improve performance and scalability.

## 📦 Features

- 🔍 Convert natural language to SQL using Google Gemini
- 📊 Query SQLite database and return structured results
- 🧠 Summarize results in human-readable explanations using LLMs
- ⚡ Redis caching for repeated queries to reduce LLM calls


---

## 🏗️ Tech Stack

- **Python 3.10+**
- **Redis** (via `redis-py`)
- **SQLite** (local database)
- **Pandas** (for CSV ingestion)
- **Google Generative AI SDK** (`google.generativeai`)
- **Gemini LLM** (used for generating SQL and summaries)

---

## 📁 Project Structure

```bash
.
├── hotel_bookings.csv             # Sample hotel booking dataset
├── hotel_bookings.db              # SQLite database (auto-generated)
├── agent.py                       # Core logic: query generation, execution, LLM calls
├── cache.py                       # Redis-based caching logic
├── README.md                      # You're here!

