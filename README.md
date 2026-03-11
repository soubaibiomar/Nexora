# Nexora — Knowledge Cartography & Expert Discovery Platform

> **AI-powered organizational intelligence** — discover experts, map skills, predict talent needs, and accelerate knowledge sharing through graph-based analytics.

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────┐
│         React Frontend           │
│  (MUI · 3D Graph · Dark Theme)  │
├──────────────────────────────────┤
│         Nginx (SPA + Proxy)      │
└───────────┬──────────────────────┘
            │ REST API
┌───────────▼──────────────────────┐
│      FastAPI Backend             │
│  ┌──────────┐ ┌───────────────┐  │
│  │ ML Engine│ │ Graph Engine  │  │
│  │ PageRank │ │ Neo4j Cypher  │  │
│  │ TF-IDF   │ │ GraphRAG      │  │
│  │ Collab.  │ └───────────────┘  │
│  │ Filter   │ ┌───────────────┐  │
│  └──────────┘ │ Kafka Sim.    │  │
│  ┌──────────┐ │ Spark Batch   │  │
│  │ Auth+RBAC│ └───────────────┘  │
│  └──────────┘                    │
└───────────┬──────────────────────┘
            │ Bolt
┌───────────▼──────────────────────┐
│       Neo4j Graph Database       │
│  (Experts · Skills · Projects)   │
└──────────────────────────────────┘
```

## ✨ Key Features

| Category | Features |
|----------|----------|
| **AI/ML** | PageRank expert scoring, skill gap prediction, emerging skill detection, future demand forecasting, cross-department collaboration suggestions, personalized recommendations, document classification (TF-IDF + Logistic Regression), AI chatbot (Veda) |
| **Graph** | 3D interactive knowledge graph, expert network visualization, relationship exploration, GraphRAG (natural language → Cypher) |
| **Big Data** | PySpark batch analytics (with Python fallback), Kafka-style pipeline simulator, skill co-occurrence matrices, department analytics |
| **Gamification** | Badges, skill endorsements, leaderboards |
| **Collaboration** | Team workspaces, real-time messaging (WebSocket), team builder |
| **Security** | JWT authentication, RBAC (admin/manager/user), rate limiting, bcrypt password hashing |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, MUI, react-force-graph-3d, Vite |
| **Backend** | FastAPI, Pydantic, Uvicorn |
| **Database** | Neo4j 5 (APOC plugin) |
| **ML** | scikit-learn, NumPy, TF-IDF, collaborative filtering, PageRank |
| **Big Data** | PySpark (optional), Kafka simulator |
| **AI** | OpenAI GPT (optional for chatbot), LangChain |
| **Auth** | JWT (python-jose), bcrypt, OAuth2 |
| **Deploy** | Docker, docker-compose, Nginx |

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and start all services
git clone <repo-url> && cd Nexora
docker-compose up --build

# Services:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# Neo4j UI:  http://localhost:7474
```

### Option 2: Local Development

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install
npm run dev

# 3. Neo4j — install and start Neo4j 5 Community
# Configure: NEO4J_URI=bolt://localhost:7687
```

### Generate Sample Data

```bash
cd data
python generate_data.py --scale large    # 2000 employees, 1000 docs, 300 projects
python generate_data.py --scale medium   # 500 employees (default)
python generate_data.py --scale small    # 100 employees
```

### Run Batch Analytics

```bash
cd backend
python -m spark.spark_batch
# Output → backend/spark/output/
```

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin | Administrator |
| demo | demo123 | User |

## 📡 API Endpoints

### Core
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/experts/search` | Search experts with filters |
| GET | `/api/documents/search` | Search documents |
| GET | `/api/graph/nodes` | Get graph nodes |
| GET | `/api/dashboard/stats` | Dashboard statistics |

### AI/ML
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/recommend-experts` | ML expert recommendation |
| GET | `/api/ai/expert-rank` | PageRank-based expert scoring |
| GET | `/api/ai/emerging-skills` | Detect emerging skill trends |
| GET | `/api/ai/future-skills?months=12` | Predict future skill demand |
| GET | `/api/ai/cross-department-suggestions` | Cross-department collaboration |
| GET | `/api/ai/personalized-recommendations/{id}` | Personalized skill recs |
| GET | `/api/ai/skill-gaps/{id}` | Skill gap analysis |
| POST | `/api/ai/chatbot` | Veda AI assistant |
| POST | `/api/ai/classify-document` | Document auto-classification |

### Big Data & Pipeline
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bigdata/skill-analytics` | Spark skill analytics |
| GET | `/api/bigdata/expert-rankings` | Expert rankings |
| POST | `/api/pipeline/simulate?count=50` | Kafka pipeline simulation |
| GET | `/api/pipeline/status` | Pipeline health metrics |

### Auth & RBAC
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/me` | Current user profile |
| GET | `/api/auth/users` | List users (admin only) |
| PUT | `/api/auth/users/{name}/role` | Update role (admin only) |

## 🧠 AI/ML Methods

### PageRank Expert Scoring
Builds a bipartite expert-skill-project graph and runs iterative PageRank (damping=0.85, 20 iterations). Final score blends graph rank (60%) with base features (40%): skill diversity, depth, project participation, document authorship, and experience.

### Skill Gap Prediction
Collaborative filtering on a user-skill matrix (cosine similarity). Finds the 10 most similar experts and recommends their skills that the target expert lacks, weighted by similarity × skill level.

### Emerging Skill Detection
Hire-date cohort analysis: compares skill adoption rates between employees hired in the last 2 years vs 2-5 years ago. Skills with >20% growth rate are flagged as "rising".

### Future Demand Forecasting
Combines project-skill demand counts with emerging-skill growth rates to project demand N months forward. Identifies critical workforce gaps where predicted demand exceeds current supply.

### Cross-Department Collaboration
Analyzes skill overlap and complementarity between departments. Identifies pairs with high complementarity scores (unique skills each could contribute) and shared foundations for collaboration.

## 📊 Data Model (Neo4j)

```
(:Expert)-[:HAS_SKILL]->(:Skill)
(:Expert)-[:WORKS_ON]->(:Project)
(:Expert)-[:AUTHORED]->(:Document)
(:Expert)-[:KNOWS]->(:Expert)
(:Project)-[:REQUIRES_SKILL]->(:Skill)
(:Document)-[:COVERS_TOPIC]->(:Topic)
```

## 📁 Project Structure

```
Nexora/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + router registration
│   │   ├── config.py            # Settings
│   │   ├── database.py          # Neo4j driver
│   │   ├── auth_utils.py        # JWT utilities
│   │   ├── routers/
│   │   │   ├── ai.py            # AI/ML endpoints
│   │   │   ├── auth.py          # Auth + RBAC
│   │   │   ├── bigdata.py       # Spark analytics endpoints
│   │   │   ├── kafka_simulator.py  # Pipeline simulation
│   │   │   ├── experts.py       # Expert CRUD
│   │   │   ├── documents.py     # Document CRUD
│   │   │   ├── graph.py         # Graph visualization
│   │   │   ├── gamification.py  # Badges & endorsements
│   │   │   └── ...
│   │   └── ml/
│   │       ├── pagerank.py      # PageRank expert scoring
│   │       ├── skill_predictor.py  # Skill gap + emerging + future
│   │       ├── recommender.py   # TF-IDF expert recommendation
│   │       ├── embeddings.py    # TF-IDF embeddings
│   │       ├── classifier.py    # Document classification
│   │       ├── chatbot.py       # Rule-based fallback
│   │       ├── summarizer.py    # LLM document summarization
│   │       └── analytics.py     # Predictive analytics
│   ├── spark/
│   │   └── spark_batch.py       # PySpark batch analytics
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── SkillEvolution.tsx  # Emerging/forecast/collaboration
│   │   │   ├── GraphVisualization.tsx  # 3D knowledge graph
│   │   │   ├── AIInsights.tsx     # AI analytics dashboard
│   │   │   ├── Dashboard.tsx      # Organization overview
│   │   │   └── ...
│   │   └── services/api.ts       # API client
│   ├── Dockerfile
│   └── nginx.conf
├── data/
│   ├── generate_data.py          # Scalable data generator
│   ├── employees.jsonl
│   ├── documents.jsonl
│   ├── projects.jsonl
│   └── skills.jsonl
├── docker-compose.yml
└── README.md
```

## 📄 License

MIT
