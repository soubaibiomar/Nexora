# 🎯 ExpertLink Intelligent

<div align="center">

**Knowledge Cartography Platform for Expert Discovery & Learning Paths**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.14+-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)

---

*An intelligent platform that leverages graph databases to map organizational knowledge, discover experts, and create personalized learning paths.*

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Neo4j Query Examples](#-neo4j-query-examples)
- [Project Structure](#-project-structure)
- [Data Model](#-data-model)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

## 🔍 Overview

ExpertLink is a comprehensive knowledge management platform designed to help organizations:

- **Identify Experts**: Find the right people with specific skills and expertise
- **Map Knowledge**: Visualize relationships between skills, projects, and team members
- **Bridge Skill Gaps**: Analyze and recommend learning paths for professional development
- **Accelerate Onboarding**: Help new employees discover mentors and resources quickly

## ✨ Features

### 🔎 Expert Search
Advanced search functionality to find experts based on:
- Skills and competencies
- Expertise level (1-5 scale)
- Geographic location
- Years of experience
- Department and role

### 📄 Document Search
Full-text search across organizational documents with:
- NLP-powered relevance scoring
- Category filtering
- Keyword highlighting
- Document-skill associations

### 🕸️ 3D Knowledge Graph
Interactive graph visualization featuring:
- Real-time 3D rendering with `react-force-graph-3d`
- Node exploration (Experts, Skills, Documents, Projects)
- Relationship discovery
- Zoom, pan, and rotate controls
- Click-to-focus navigation

### 📚 Learning Paths
Personalized skill development with:
- AI-recommended learning sequences
- Skill prerequisites mapping
- Progress tracking
- Resource recommendations
- Time estimates for skill acquisition

### 📊 Analytics Dashboard
Comprehensive analytics including:
- Skill distribution charts
- Top skills in demand
- Expert availability metrics
- Knowledge gap analysis
- Skill trend visualization

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async API framework |
| **Neo4j** | Graph database for relationship modeling |
| **Pydantic** | Data validation and serialization |
| **python-jose** | JWT authentication |
| **Uvicorn** | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI component library |
| **TypeScript** | Type-safe JavaScript |
| **Material-UI (MUI)** | Component design system |
| **react-force-graph-3d** | 3D graph visualization |
| **Recharts** | Data visualization charts |
| **Axios** | HTTP client |
| **Vite** | Build tool and dev server |

### Database
| Technology | Purpose |
|------------|---------|
| **Neo4j 5.x** | Primary graph database |
| **Cypher** | Graph query language |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │Dashboard │ │ Expert   │ │Document  │ │  Graph   │ │Learning│ │
│  │          │ │ Search   │ │ Search   │ │   Viz    │ │  Path  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬───┘ │
└───────┼────────────┼────────────┼────────────┼────────────┼─────┘
        │            │            │            │            │
        └────────────┴─────┬──────┴────────────┴────────────┘
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │/dashboard│ │/experts  │ │/documents│ │ /graph   │ │/learning│ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬───┘ │
└───────┼────────────┼────────────┼────────────┼────────────┼─────┘
        │            │            │            │            │
        └────────────┴─────┬──────┴────────────┴────────────┘
                           │ Cypher Queries
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Neo4j Database                           │
│   ┌───────┐      ┌───────┐      ┌─────────┐      ┌─────────┐   │
│   │Expert │──────│ Skill │──────│Document │──────│ Project │   │
│   └───────┘      └───────┘      └─────────┘      └─────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Neo4j 5.x (or Docker)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd expertlink-main
```

### 2. Setup Neo4j Database

**Option A: Using Docker (Recommended)**
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:latest
```

**Option B: Local Installation**
1. Download Neo4j from [neo4j.com/download](https://neo4j.com/download)
2. Install and start the service
3. Set password to `password` (or update `.env`)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env with your Neo4j credentials

# Import sample data into Neo4j
python scripts/import_data.py

# Run the API server
uvicorn app.main:app --reload --port 8000
```

### 5. Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# Neo4j Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=true
CORS_ORIGINS=http://localhost:5173
```

### 6. Default Test Credentials

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `password` | Administrator | Full access to all features |
| `user` | `password` | User | Standard user access |

### 7. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 8. Access the Application

| Service | URL |
|---------|-----|
| 🖥️ **Frontend** | http://localhost:5173 |
| 📖 **API Docs (Swagger)** | http://localhost:8000/docs |
| 📖 **API Docs (ReDoc)** | http://localhost:8000/redoc |
| 🗄️ **Neo4j Browser** | http://localhost:7474 |

## 📖 API Documentation

### Authentication

```bash
# Login
POST /api/auth/login
Content-Type: application/json
{
  "username": "admin",
  "password": "password"
}
```

### Experts API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/experts` | List all experts |
| GET | `/api/experts/{id}` | Get expert by ID |
| GET | `/api/experts/search?q={query}` | Search experts |
| GET | `/api/experts/{id}/skills` | Get expert's skills |
| POST | `/api/experts` | Create new expert |
| PUT | `/api/experts/{id}` | Update expert |
| DELETE | `/api/experts/{id}` | Delete expert |

### Documents API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents` | List all documents |
| GET | `/api/documents/{id}` | Get document by ID |
| GET | `/api/documents/search?q={query}` | Full-text search |
| GET | `/api/documents/category/{cat}` | Filter by category |

### Graph API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/graph/nodes` | Get all graph nodes |
| GET | `/api/graph/edges` | Get all relationships |
| GET | `/api/graph/neighbors/{id}` | Get node neighbors |

### Learning API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/learning/paths` | Get learning paths |
| GET | `/api/learning/skills/{skill}/prerequisites` | Get skill prerequisites |
| POST | `/api/learning/recommend` | Get AI recommendations |

### Dashboard API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get general statistics |
| GET | `/api/dashboard/skills/distribution` | Skill distribution |
| GET | `/api/dashboard/top-skills` | Most common skills |

## 🔍 Neo4j Query Examples

The platform implements all required Neo4j query patterns:

### Simple Query
```cypher
// Find all experts
MATCH (e:Expert)
RETURN e.name, e.title, e.department
LIMIT 10
```

### Path Query
```cypher
// Find shortest path between expert and skill
MATCH path = shortestPath(
  (e:Expert {name: "John Doe"})-[*]-(s:Skill {name: "Python"})
)
RETURN path
```

### Aggregation Query
```cypher
// Count experts per skill
MATCH (e:Expert)-[:HAS_SKILL]->(s:Skill)
RETURN s.name AS skill, count(e) AS expert_count
ORDER BY expert_count DESC
```

### Filter Query
```cypher
// Find senior experts (level >= 4)
MATCH (e:Expert)-[r:HAS_SKILL]->(s:Skill)
WHERE r.level >= 4
RETURN e.name, s.name, r.level
```

### Modification Query
```cypher
// Update expert's skill level
MATCH (e:Expert {id: $expertId})-[r:HAS_SKILL]->(s:Skill {id: $skillId})
SET r.level = $newLevel
RETURN e, s
```

## 📁 Project Structure

```
ExpertLink/
├── 📂 backend/
│   ├── 📂 app/
│   │   ├── 📄 main.py              # FastAPI application entry
│   │   ├── 📄 database.py          # Neo4j connection manager
│   │   ├── 📄 config.py            # Settings & configuration
│   │   ├── 📄 auth_utils.py        # JWT authentication
│   │   ├── 📄 fallback_data.py     # Fallback data when DB unavailable
│   │   ├── 📂 models/              # Pydantic data models
│   │   │   ├── 📄 expert.py
│   │   │   ├── 📄 document.py
│   │   │   └── 📄 skill.py
│   │   └── 📂 routers/             # API route handlers
│   │       ├── 📄 auth.py          # Authentication endpoints
│   │       ├── 📄 dashboard.py     # Dashboard analytics
│   │       ├── 📄 documents.py     # Document CRUD
│   │       ├── 📄 experts.py       # Expert CRUD
│   │       ├── 📄 graph.py         # Graph visualization
│   │       └── 📄 learning.py      # Learning paths
│   ├── 📂 scripts/
│   │   └── 📄 import_data.py       # Data import utility
│   └── 📄 requirements.txt         # Python dependencies
│
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── 📄 App.tsx              # Main React component
│   │   ├── 📄 main.tsx             # Application entry
│   │   ├── 📂 pages/               # Page components
│   │   │   ├── 📄 Dashboard.tsx    # Analytics dashboard
│   │   │   ├── 📄 ExpertSearch.tsx # Expert search UI
│   │   │   ├── 📄 DocumentSearch.tsx
│   │   │   ├── 📄 GraphVisualization.tsx
│   │   │   ├── 📄 LearningPath.tsx
│   │   │   └── 📄 Login.tsx
│   │   ├── 📂 services/            # API client
│   │   │   └── 📄 api.ts
│   │   └── 📂 theme/               # MUI theme
│   │       └── 📄 theme.ts
│   ├── 📄 package.json
│   └── 📄 vite.config.ts
│
├── 📂 data/                        # Sample JSONL data
│   ├── 📄 employees.jsonl          # Expert profiles
│   ├── 📄 documents.jsonl          # Document metadata
│   ├── 📄 skills.jsonl             # Skill taxonomy
│   ├── 📄 projects.jsonl           # Project information
│   └── 📄 generate_data.py         # Data generation script
│
├── 📂 rapport/                     # Project documentation
│   └── 📄 rapport_expertlink.tex   # LaTeX report
│
└── 📄 README.md
```

## 📊 Data Model

### Graph Schema

```
(:Expert)
  - id: string
  - name: string
  - email: string
  - title: string
  - department: string
  - location: string
  - years_experience: int
  - avatar: string

(:Skill)
  - id: string
  - name: string
  - category: string
  - description: string

(:Document)
  - id: string
  - title: string
  - content: string
  - category: string
  - author: string
  - created_at: datetime

(:Project)
  - id: string
  - name: string
  - description: string
  - status: string
  - start_date: date
  - end_date: date

Relationships:
  (Expert)-[:HAS_SKILL {level: int}]->(Skill)
  (Expert)-[:WORKS_ON {role: string}]->(Project)
  (Expert)-[:AUTHORED]->(Document)
  (Document)-[:RELATES_TO]->(Skill)
  (Skill)-[:PREREQUISITE_OF]->(Skill)
  (Project)-[:REQUIRES]->(Skill)
```

## 🖼️ Screenshots

### Login Page
Secure authentication interface with modern design.

![Login Page](rapport/images/login_page.png)

### Dashboard
Analytics overview with skill distribution charts, top experts, and key metrics.

![Dashboard](rapport/images/dashboard.png)

### Expert Search
Advanced filtering and search capabilities for finding the right experts by skills, department, and experience level.

![Expert Search](rapport/images/expert_search.png)

### Document Search
Full-text search across organizational documents with category filtering and relevance scoring.

![Document Search](rapport/images/document_search.png)

### 3D Knowledge Graph
Interactive 3D visualization of the entire knowledge network showing relationships between experts, skills, documents, and projects.

![Knowledge Graph](rapport/images/graph_visualization.png)

### Learning Paths
Personalized recommendations for skill development with progress tracking and resource suggestions.

![Learning Paths](rapport/images/learning_path.png)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for TypeScript/React
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📝 License

MIT License - Université 2025/2026

---

<div align="center">

**Built with ❤️ for Knowledge Management**

*ExpertLink - Université 2025/2026*

</div>
