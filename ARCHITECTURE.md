# Nexora — System Architecture

## Data Flow Overview

```mermaid
graph TB
    subgraph Frontend["Frontend (React + Vite)"]
        UI[UI Components]
        API_SVC[API Service Layer]
        GRAPH_3D[3D Graph Engine]
    end

    subgraph Backend["Backend (FastAPI)"]
        ROUTER[API Routers]
        ML[ML Engine]
        AUTH[Auth + RBAC]
        PIPE[Kafka Simulator]
    end

    subgraph ML_Models["ML Models"]
        PR[PageRank]
        SP[Skill Predictor]
        REC[Recommender]
        CLS[Classifier]
        EMB[Embeddings]
    end

    subgraph Data["Data Layer"]
        NEO4J[(Neo4j)]
        JSONL[(JSONL Files)]
        SPARK[Spark Batch]
    end

    UI --> API_SVC --> ROUTER
    GRAPH_3D --> API_SVC
    ROUTER --> ML
    ROUTER --> AUTH
    ROUTER --> PIPE
    ML --> PR & SP & REC & CLS & EMB
    ROUTER --> NEO4J
    ML --> JSONL
    SPARK --> JSONL
```

## Request Lifecycle

```
Client → Nginx (port 3000)
  ├─ /api/* → Proxy → FastAPI (port 8000) → Neo4j/ML/JSONL
  └─ /*     → React SPA (index.html fallback)
```

## ML Pipeline Architecture

```mermaid
graph LR
    DATA[JSONL Data] --> TRAIN[Model Training]
    TRAIN --> USM[User-Skill Matrix]
    TRAIN --> TFIDF[TF-IDF Vectors]
    TRAIN --> GRAPH[Expert-Skill Graph]

    USM --> CF[Collaborative Filtering]
    CF --> GAPS[Skill Gap Prediction]
    CF --> EMERGING[Emerging Skills]
    CF --> FUTURE[Future Demand]

    TFIDF --> REC[Expert Recommendation]
    TFIDF --> CLS[Document Classification]
    TFIDF --> SIM[Text Similarity]

    GRAPH --> RANK[PageRank Scoring]
    RANK --> EXPERT_RANK[Expert Influence]
```

## Authentication & RBAC Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant N as Nginx
    participant F as FastAPI
    participant J as JWT

    C->>N: POST /api/auth/login
    N->>F: Proxy request
    F->>F: Verify credentials (bcrypt)
    F->>F: Check rate limit
    F->>J: Sign JWT (sub + role)
    J-->>F: Token
    F-->>C: {access_token, role}

    C->>N: GET /api/auth/users (Authorization: Bearer ...)
    N->>F: Proxy request
    F->>J: Decode & verify token
    J-->>F: {sub: "admin", role: "admin"}
    F->>F: require_role("admin") check
    F-->>C: User list (200 OK)
```

## Big Data Pipeline

```mermaid
graph LR
    subgraph Ingestion["Kafka Simulator"]
        EVT[Events] --> QUEUE[Event Queue]
        QUEUE --> PROC[Processor]
        PROC --> METRICS[Metrics]
    end

    subgraph Batch["Spark Batch Job"]
        JSONL[JSONL Files] --> SPARK[PySpark / Python]
        SPARK --> SK_A[Skill Analytics]
        SPARK --> DOC_A[Document Analytics]
        SPARK --> EXP_A[Expert Rankings]
        SPARK --> DEPT_A[Department Analytics]
        SPARK --> PROJ_A[Project Analytics]
    end

    SK_A & DOC_A & EXP_A & DEPT_A & PROJ_A --> OUTPUT[spark/output/*.json]
    OUTPUT --> BIGDATA_API[/api/bigdata/* endpoints]
```

## Deployment Architecture (Docker)

```
docker-compose.yml
├── neo4j (port 7474, 7687)
│   └── Persistent volume: neo4j_data
├── backend (port 8000)
│   ├── FastAPI + Uvicorn
│   ├── Mounts: ./data → /app/data
│   └── Depends: neo4j (healthcheck)
└── frontend (port 3000 → 80)
    ├── Build: Node 20 → Nginx Alpine
    ├── SPA routing + API proxy
    └── Depends: backend
```

## Neo4j Schema

| Node | Properties |
|------|-----------|
| Expert | id, name, email, department, role, location, experience_years, expertise_level |
| Skill | id, name, category, level, demand |
| Document | id, title, type, topic, content, author, date, views, rating |
| Project | id, name, domain, tech_stack, status, budget, priority |

| Relationship | Direction |
|-------------|-----------|
| HAS_SKILL | Expert → Skill |
| WORKS_ON | Expert → Project |
| AUTHORED | Expert → Document |
| KNOWS | Expert → Expert |
| REQUIRES_SKILL | Project → Skill |
