<div align="center">

# 🏗️ ExpertLink - Documentation Technique Complète

**Plateforme de Cartographie des Connaissances avec Neo4j**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org)
[![Neo4j](https://img.shields.io/badge/Database-Neo4j-008CC1?style=for-the-badge&logo=neo4j)](https://neo4j.com)

---

</div>

## 📋 Table des Matières

1. [Vue d&#39;Ensemble](#-vue-densemble)
2. [Architecture 3-Tiers](#-architecture-3-tiers)
3. [Connexions entre Composants](#-connexions-entre-composants)
4. [Description Détaillée des Fichiers Backend](#-description-détaillée-des-fichiers-backend)
5. [Description Détaillée des Fichiers Frontend](#-description-détaillée-des-fichiers-frontend)
6. [Les 5 Types de Requêtes Cypher](#-les-5-types-de-requêtes-cypher)
7. [Flux de Données Complet](#-flux-de-données-complet)
8. [Démarrage du Projet](#-démarrage-du-projet)

---

## 🎯 Vue d'Ensemble

### Qu'est-ce qu'ExpertLink ?

**ExpertLink** est une plateforme de gestion des connaissances organisationnelles qui permet de :

| Fonctionnalité                      | Description                                                            |
| ------------------------------------ | ---------------------------------------------------------------------- |
| 🔍**Recherche d'Experts**      | Trouver des spécialistes par compétences, localisation, département |
| 📄**Recherche de Documents**   | Recherche plein texte avec filtres par type et catégorie              |
| 🕸️**Visualisation 3D**       | Graphe interactif des relations entre experts, skills, projets         |
| 📚**Parcours d'Apprentissage** | Génération de chemins de formation personnalisés                    |
| 📊**Tableau de Bord**          | Statistiques et analyses sur les compétences                          |

### Pourquoi Neo4j ?

Neo4j est une **base de données orientée graphe** idéale pour ce projet car :

- ✅ Les relations entre entités (experts, skills, projets) sont **naturellement modélisées**
- ✅ Les requêtes de **navigation** (trouver le chemin entre 2 experts) sont très performantes
- ✅ Le langage **Cypher** est intuitif et expressif
- ✅ Parfait pour les **recommandations** (experts similaires, skills complémentaires)

---

## 🏛️ Architecture 3-Tiers

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        COUCHE PRÉSENTATION (Frontend)                         ║
║                              http://localhost:5173                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   L'utilisateur interagit avec l'interface React                              ║
║   → Les composants appellent les services API (api.ts)                        ║
║   → Axios envoie des requêtes HTTP au backend                                 ║
║                                                                               ║
║   Technologies: React 18, TypeScript, Material-UI, Axios, react-force-graph   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      │ REST API (HTTP/JSON)
                                      │ Port 5173 → Port 8000
                                      ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         COUCHE MÉTIER (Backend)                               ║
║                              http://localhost:8000                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   FastAPI reçoit les requêtes HTTP                                            ║
║   → Valide les données avec Pydantic                                          ║
║   → Construit des requêtes Cypher dynamiques                                  ║
║   → Exécute les requêtes sur Neo4j                                            ║
║   → Retourne les résultats en JSON                                            ║
║                                                                               ║
║   Technologies: FastAPI, Pydantic, python-jose (JWT), Neo4j Driver            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      │ Cypher Queries (Protocole Bolt)
                                      │ Port 8000 → Port 7687
                                      ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         COUCHE DONNÉES (Database)                             ║
║                         bolt://localhost:7687                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   Neo4j stocke et gère les données sous forme de graphe                       ║
║                                                                               ║
║   Nœuds (Nodes):                                                              ║
║     • Person (Experts/Employés)                                               ║
║     • Skill (Compétences)                                                     ║
║     • Document (Articles, Tutoriels)                                          ║
║     • Project (Projets de l'entreprise)                                       ║
║                                                                               ║
║   Relations:                                                                  ║
║     • (Person)-[:HAS_SKILL]->(Skill)                                          ║
║     • (Person)-[:WORKS_ON]->(Project)                                         ║
║     • (Person)-[:AUTHORED]->(Document)                                        ║
║     • (Document)-[:COVERS_TOPIC]->(Skill)                                     ║
║     • (Project)-[:REQUIRES]->(Skill)                                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 🔗 Connexions entre Composants

### 1. Frontend → Backend (HTTP/REST)

```
┌─────────────────┐         HTTP Request          ┌─────────────────┐
│                 │  ─────────────────────────▶  │                 │
│   React App     │   GET /api/experts/search    │   FastAPI       │
│   (Port 5173)   │   Authorization: Bearer xxx   │   (Port 8000)   │
│                 │  ◀─────────────────────────  │                 │
└─────────────────┘       JSON Response           └─────────────────┘
```

**Fichier responsable:** `frontend/src/services/api.ts`

```typescript
// Configuration du client HTTP
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: { 'Content-Type': 'application/json' }
});

// Ajout automatique du token JWT à chaque requête
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
```

### 2. Backend → Database (Bolt Protocol)

```
┌─────────────────┐         Cypher Query          ┌─────────────────┐
│                 │  ─────────────────────────▶  │                 │
│   FastAPI       │   MATCH (p:Person) RETURN p  │   Neo4j         │
│   (Port 8000)   │                               │   (Port 7687)   │
│                 │  ◀─────────────────────────  │                 │
└─────────────────┘      Records (Nodes/Rels)     └─────────────────┘
```

**Fichier responsable:** `backend/app/database.py`

```python
# Création du driver Neo4j (connexion persistante)
class Neo4jDriver:
    @classmethod
    def get_driver(cls):
        cls._driver = GraphDatabase.driver(
            "bolt://localhost:7687",      # URI Neo4j
            auth=("neo4j", "password")    # Credentials
        )
        return cls._driver

# Injection de dépendance pour les routes
def get_db():
    driver = Neo4jDriver.get_driver()
    session = driver.session()
    try:
        yield session  # Fourni aux endpoints
    finally:
        session.close()  # Nettoyage automatique
```

---



## 📁 Description Détaillée des Fichiers Backend

### Structure du dossier `backend/`

```
backend/
├── app/
│   ├── __init__.py          # Initialisation du package
│   ├── main.py              # Point d'entrée de l'application
│   ├── database.py          # Gestion de la connexion Neo4j
│   ├── config.py            # Configuration et variables d'environnement
│   ├── auth_utils.py        # Utilitaires d'authentification JWT
│   ├── fallback_data.py     # Données de secours (si Neo4j indisponible)
│   ├── models/              # Modèles Pydantic
│   └── routers/             # Contrôleurs API
│       ├── auth.py
│       ├── experts.py
│       ├── documents.py
│       ├── graph.py
│       ├── dashboard.py
│       └── learning.py
├── scripts/
│   └── import_data.py       # Script d'importation des données
└── requirements.txt         # Dépendances Python
```

---

### 📄 `main.py` - Point d'Entrée de l'Application

**Utilité:** Configure et démarre l'application FastAPI.

| Responsabilité              | Description                                                        |
| ---------------------------- | ------------------------------------------------------------------ |
| **Création de l'app** | Initialise FastAPI avec titre, description, version                |
| **CORS**               | Configure les origines autorisées (localhost:5173)                |
| **Routers**            | Enregistre tous les endpoints (/api/experts, /api/documents, etc.) |
| **Lifespan**           | Gère le démarrage/arrêt (fermeture du driver Neo4j)             |

```python
app = FastAPI(
    title="ExpertLink Intelligent",
    description="Knowledge Cartography Platform",
    version="1.0.0"
)

# Enregistrement des routes
app.include_router(experts.router)   # /api/experts/*
app.include_router(documents.router) # /api/documents/*
app.include_router(graph.router)     # /api/graph/*
app.include_router(dashboard.router) # /api/dashboard/*
app.include_router(learning.router)  # /api/learning/*
app.include_router(auth.router)      # /api/auth/*
```

---

### 📄 `database.py` - Connexion Neo4j

**Utilité:** Gère la connexion à la base de données Neo4j.

| Fonction/Classe          | Utilité                                                 |
| ------------------------ | -------------------------------------------------------- |
| `Neo4jDriver`          | Singleton qui maintient une connexion unique au driver   |
| `get_driver()`         | Retourne le driver Neo4j (le crée si nécessaire)       |
| `close()`              | Ferme proprement la connexion                            |
| `is_neo4j_available()` | Vérifie si Neo4j est accessible                         |
| `get_db()`             | Fournit une session aux endpoints (dependency injection) |
| `FallbackSession`      | Session mock quand Neo4j est indisponible                |

```python
# Vérification de disponibilité
def is_neo4j_available() -> bool:
    try:
        driver = Neo4jDriver.get_driver()
        with driver.session() as session:
            session.run("RETURN 1")  # Test simple
        return True
    except Exception:
        return False

# Injection dans les routes
@router.get("/search")
async def search(db=Depends(get_db)):  # 'db' reçoit la session
    result = db.run("MATCH (p:Person) RETURN p")
    ...
```

---

### 📄 `config.py` - Configuration

**Utilité:** Centralise toutes les variables de configuration.

| Variable                        | Valeur par défaut        | Description                       |
| ------------------------------- | ------------------------- | --------------------------------- |
| `neo4j_uri`                   | `bolt://localhost:7687` | URI de connexion Neo4j            |
| `neo4j_user`                  | `neo4j`                 | Nom d'utilisateur                 |
| `neo4j_password`              | `expertlink123`         | Mot de passe                      |
| `secret_key`                  | (généré)               | Clé secrète pour signer les JWT |
| `algorithm`                   | `HS256`                 | Algorithme de signature JWT       |
| `access_token_expire_minutes` | `30`                    | Durée de validité du token      |
| `debug`                       | `False`                 | Mode debug                        |

```python
class Settings(BaseSettings):
    neo4j_uri: str = Field("bolt://localhost:7687")
    neo4j_user: str = Field("neo4j")
    secret_key: str = Field("your-super-secret-key")
  
    model_config = SettingsConfigDict(
        env_file=".env",  # Charge depuis fichier .env
        case_sensitive=False
    )
```

---

### 📄 `auth_utils.py` - Authentification JWT

**Utilité:** Gère la création et validation des tokens JWT.

| Fonction                  | Utilité                                    |
| ------------------------- | ------------------------------------------- |
| `create_access_token()` | Génère un token JWT avec expiration       |
| `get_current_user()`    | Vérifie le token et retourne l'utilisateur |

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.secret_key)
    username = payload.get("sub")
    if username != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return username
```

---

### 📄 `fallback_data.py` - Données de Secours

**Utilité:** Fournit des données depuis des fichiers JSONL quand Neo4j est indisponible.

| Fonction                  | Description                                 |
| ------------------------- | ------------------------------------------- |
| `load_jsonl(filename)`  | Charge et cache un fichier JSONL            |
| `get_employees()`       | Retourne tous les employés                 |
| `get_documents()`       | Retourne tous les documents                 |
| `get_skills()`          | Retourne tous les skills                    |
| `get_projects()`        | Retourne tous les projets                   |
| `search_experts(...)`   | Recherche avec filtres (en mémoire)        |
| `search_documents(...)` | Recherche documents avec filtres            |
| `get_dashboard_stats()` | Calcule les statistiques                    |
| `get_graph_data()`      | Génère les données pour la visualisation |

```python
# Exemple d'utilisation dans un router
@router.get("/search")
async def search_experts(db=Depends(get_db)):
    if not is_neo4j_available():
        # Neo4j indisponible → utiliser les données locales
        return fallback_data.search_experts(q=q, limit=limit)
  
    # Neo4j disponible → requête Cypher normale
    result = db.run("MATCH (p:Person) RETURN p")
    ...
```

---

### 📂 `routers/` - Les Contrôleurs API

#### 📄 `experts.py` - Gestion des Experts

| Endpoint                          | Méthode | Description                      | Type Requête               |
| --------------------------------- | -------- | -------------------------------- | --------------------------- |
| `/api/experts/search`           | GET      | Recherche avec filtres multiples | **RF** (Filter)       |
| `/api/experts/{id}`             | GET      | Profil complet d'un expert       | **RS** (Simple)       |
| `/api/experts/{id}/network`     | GET      | Réseau de connexions            | **RC** (Chemin)       |
| `/api/experts`                  | POST     | Créer un expert                 | **RM** (Modification) |
| `/api/experts/{id}`             | PUT      | Modifier un expert               | **RM** (Modification) |
| `/api/experts/{id}`             | DELETE   | Supprimer un expert              | **RM** (Modification) |
| `/api/experts/locations/list`   | GET      | Liste des localisations          | **RS** (Simple)       |
| `/api/experts/departments/list` | GET      | Liste des départements          | **RS** (Simple)       |

---

#### 📄 `documents.py` - Gestion des Documents

| Endpoint                        | Méthode | Description               | Type Requête               |
| ------------------------------- | -------- | ------------------------- | --------------------------- |
| `/api/documents/search`       | GET      | Recherche full-text       | **RF** (Filter)       |
| `/api/documents/{id}`         | GET      | Détails d'un document    | **RS** (Simple)       |
| `/api/documents/similar/{id}` | GET      | Documents similaires      | **RC** (Chemin)       |
| `/api/documents/experts/{id}` | GET      | Experts liés au document | **RC** (Chemin)       |
| `/api/documents/types/list`   | GET      | Types de documents        | **RS** (Simple)       |
| `/api/documents`              | POST     | Créer un document        | **RM** (Modification) |
| `/api/documents/{id}`         | PUT      | Modifier un document      | **RM** (Modification) |
| `/api/documents/{id}`         | DELETE   | Supprimer un document     | **RM** (Modification) |

---

#### 📄 `graph.py` - Visualisation du Graphe

| Endpoint                   | Méthode | Description                 | Type Requête              |
| -------------------------- | -------- | --------------------------- | -------------------------- |
| `/api/graph/nodes`       | GET      | Récupérer les nœuds      | **RS** (Simple)      |
| `/api/graph/expand/{id}` | GET      | Étendre un nœud (voisins) | **RC** (Chemin)      |
| `/api/graph/path`        | GET      | Chemin le plus court        | **RC** (Chemin)      |
| `/api/graph/stats`       | GET      | Statistiques du graphe      | **RA** (Agrégation) |

---

#### 📄 `dashboard.py` - Tableau de Bord

| Endpoint                              | Méthode | Description             | Type Requête               |
| ------------------------------------- | -------- | ----------------------- | --------------------------- |
| `/api/dashboard/stats`              | GET      | Statistiques globales   | **RA** (Agrégation)  |
| `/api/dashboard/top-skills`         | GET      | Top compétences        | **RA** (Agrégation)  |
| `/api/dashboard/skill-gaps`         | GET      | Lacunes de compétences | **RA** + **RF** |
| `/api/dashboard/departments`        | GET      | Stats par département  | **RA** (Agrégation)  |
| `/api/dashboard/skill-distribution` | GET      | Distribution des skills | **RA** (Agrégation)  |
| `/api/dashboard/project-status`     | GET      | Status des projets      | **RA** (Agrégation)  |
| `/api/dashboard/collaboration-rate` | GET      | Taux de collaboration   | **RC** (Chemin)       |
| `/api/dashboard/knowledge-silos`    | GET      | Silos de connaissances  | **RA** + **RF** |

---

#### 📄 `learning.py` - Parcours d'Apprentissage

| Endpoint                             | Méthode | Description              | Type Requête               |
| ------------------------------------ | -------- | ------------------------ | --------------------------- |
| `/api/learning/path`               | POST     | Générer un parcours    | **RC** (Chemin)       |
| `/api/learning/mentors/{skill}`    | GET      | Mentors pour un skill    | **RF** + **RA** |
| `/api/learning/skills/recommended` | GET      | Skills recommandés      | **RC** + **RA** |
| `/api/learning/skills/list`        | GET      | Liste de tous les skills | **RS** (Simple)       |

---

#### 📄 `auth.py` - Authentification

| Endpoint            | Méthode | Description              |
| ------------------- | -------- | ------------------------ |
| `/api/auth/login` | POST     | Connexion (retourne JWT) |

---

## 🖥️ Description Détaillée des Fichiers Frontend

### Structure du dossier `frontend/`

```
frontend/
├── src/
│   ├── main.tsx              # Point d'entrée React
│   ├── App.tsx               # Composant principal + Routing
│   ├── App.css               # Styles globaux
│   ├── index.css             # Reset CSS
│   ├── services/
│   │   └── api.ts            # Client HTTP (Axios)
│   ├── pages/
│   │   ├── Login.tsx         # Page de connexion
│   │   ├── Dashboard.tsx     # Tableau de bord
│   │   ├── ExpertSearch.tsx  # Recherche d'experts
│   │   ├── DocumentSearch.tsx # Recherche de documents
│   │   ├── GraphVisualization.tsx # Graphe 3D
│   │   └── LearningPath.tsx  # Parcours d'apprentissage
│   └── theme/
│       └── theme.ts          # Configuration Material-UI
├── package.json              # Dépendances npm
├── vite.config.ts            # Configuration Vite
└── tsconfig.json             # Configuration TypeScript
```

---

### 📄 `main.tsx` - Point d'Entrée

**Utilité:** Initialise React et monte l'application dans le DOM.

```typescript
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

---

### 📄 `App.tsx` - Composant Principal

**Utilité:** Gère le routing et la structure globale de l'application.

| Responsabilité      | Description                                              |
| -------------------- | -------------------------------------------------------- |
| **Routing**    | Définit les routes (/login, /experts, /documents, etc.) |
| **Layout**     | Barre de navigation, menu latéral                       |
| **Auth Guard** | Redirige vers /login si non authentifié                 |
| **Theme**      | Applique le thème Material-UI                           |

```typescript
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/" element={<Dashboard />} />
  <Route path="/experts" element={<ExpertSearch />} />
  <Route path="/documents" element={<DocumentSearch />} />
  <Route path="/graph" element={<GraphVisualization />} />
  <Route path="/learning" element={<LearningPath />} />
</Routes>
```

---

### 📄 `api.ts` - Client HTTP

**Utilité:** Centralise toutes les communications avec le backend.

| Service              | Méthodes                                               | Description            |
| -------------------- | ------------------------------------------------------- | ---------------------- |
| `authService`      | `login()`, `logout()`, `isAuthenticated()`        | Authentification       |
| `expertService`    | `search()`, `getById()`, `update()`, `delete()` | Gestion experts        |
| `documentService`  | `search()`, `getById()`, `getSimilar()`           | Gestion documents      |
| `graphService`     | `getNodes()`, `expand()`, `findPath()`            | Visualisation graphe   |
| `learningService`  | `generatePath()`, `getMentors()`                    | Parcours apprentissage |
| `dashboardService` | `getStats()`, `getTopSkills()`                      | Statistiques           |

---

### 📂 `pages/` - Les Pages

#### 📄 `Login.tsx` (4.5 KB)

**Utilité:** Formulaire de connexion avec validation.

- Champs: username, password
- Appelle `authService.login()`
- Stocke le token dans localStorage
- Redirige vers Dashboard après succès

---

#### 📄 `Dashboard.tsx` (19 KB)

**Utilité:** Affiche les statistiques et métriques globales.

| Widget             | Source API                 | Description                           |
| ------------------ | -------------------------- | ------------------------------------- |
| Cartes de stats    | `getStats()`             | Nombre d'experts, skills, documents   |
| Top Skills         | `getTopSkills()`         | Graphique des compétences demandées |
| Skill Distribution | `getSkillDistribution()` | PieChart par catégorie               |
| Departments        | `getDepartments()`       | Stats par département                |

---

#### 📄 `ExpertSearch.tsx` (41 KB)

**Utilité:** Interface de recherche avancée des experts.

| Fonctionnalité                 | Description                               |
| ------------------------------- | ----------------------------------------- |
| **Barre de recherche**    | Recherche par nom, rôle                  |
| **Filtres avancés**      | Skill, niveau, département, localisation |
| **Tableau de résultats** | Affichage paginé des résultats          |
| **Détails expert**       | Modal avec profil complet                 |
| **Actions**               | Voir, Modifier, Supprimer                 |

---

#### 📄 `DocumentSearch.tsx` (20 KB)

**Utilité:** Recherche full-text dans les documents.

| Fonctionnalité                | Description                      |
| ------------------------------ | -------------------------------- |
| **Recherche texte**      | Dans titre, contenu, topic       |
| **Filtres**              | Type de document, note minimum   |
| **Résultats**           | Cards avec aperçu               |
| **Documents similaires** | Suggestions basées sur le topic |

---

#### 📄 `GraphVisualization.tsx` (13 KB)

**Utilité:** Visualisation 3D interactive du graphe de connaissances.

| Fonctionnalité               | Description                              |
| ----------------------------- | ---------------------------------------- |
| **Rendu 3D**            | Utilise react-force-graph-3d             |
| **Nœuds colorés**     | Par type (Person=bleu, Skill=vert, etc.) |
| **Expansion**           | Click pour voir les connexions           |
| **Recherche de chemin** | Trouver le lien entre 2 nœuds           |
| **Navigation**          | Zoom, rotation, pan                      |

---

#### 📄 `LearningPath.tsx` (25 KB)

**Utilité:** Génération de parcours d'apprentissage personnalisés.

| Fonctionnalité                     | Description                           |
| ----------------------------------- | ------------------------------------- |
| **Sélection skills actuels** | Choisir les compétences maîtrisées |
| **Skill cible**               | Compétence à acquérir              |
| **Génération du parcours**  | Étapes avec durée estimée          |
| **Ressources**                | Documents recommandés par étape     |
| **Mentors**                   | Experts disponibles pour chaque skill |

---

## 📊 Les 5 Types de Requêtes Cypher

### Tableau Récapitulatif

|     Code     | Nom                   | Description                        | Exemple Cypher                | Fichiers                         |
| :----------: | --------------------- | ---------------------------------- | ----------------------------- | -------------------------------- |
| **RS** | Requête Simple       | Récupérer des nœuds sans filtre | `MATCH (p:Person) RETURN p` | `graph.py`, `experts.py`     |
| **RC** | Requête Chemin       | Navigation via relations           | `shortestPath((a)-[*]-(b))` | `graph.py`, `learning.py`    |
| **RF** | Requête Filtre       | Conditions WHERE                   | `WHERE p.level >= 4`        | `experts.py`, `documents.py` |
| **RA** | Requête Agrégation  | Statistiques avec count, avg       | `count(p) as total`         | `dashboard.py`                 |
| **RM** | Requête Modification | CREATE, SET, DELETE                | `SET p.name = $name`        | `experts.py`, `documents.py` |

---

### 1️⃣ RS: Requête Simple (Select All)

**But:** Récupérer tous les nœuds d'un type donné sans conditions.

```cypher
-- Tous les experts
MATCH (p:Person)
RETURN p.id, p.name, p.email, p.department
LIMIT 100

-- Toutes les localisations uniques
MATCH (p:Person)
RETURN DISTINCT p.location
ORDER BY p.location
```

**Fichier:** `backend/app/routers/experts.py` ligne 270-285

---

### 2️⃣ RC: Requête Chemin (Relation)

**But:** Naviguer à travers les relations entre nœuds.

```cypher
-- Chemin le plus court entre deux experts
MATCH (start {id: $from_id}), (end {id: $to_id})
MATCH path = shortestPath((start)-[*..6]-(end))
RETURN nodes(path), length(path)

-- Réseau d'un expert (jusqu'à 3 sauts)
MATCH path = (p:Person {id: $id})-[*1..3]->(connected)
WHERE connected:Skill OR connected:Project
RETURN nodes(path), relationships(path)
```

**Fichier:** `backend/app/routers/graph.py` ligne 114-152

---

### 3️⃣ RF: Requête Filtre (Filter)

**But:** Appliquer des conditions pour filtrer les résultats.

```cypher
-- Experts avec plusieurs critères
MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
WHERE p.expertise_level >= $level 
  AND p.location = $location
  AND p.department = $department
  AND toLower(s.name) CONTAINS toLower($skill)
RETURN DISTINCT p.name, p.department
ORDER BY p.expertise_level DESC
SKIP $skip LIMIT $limit
```

**Fichier:** `backend/app/routers/experts.py` ligne 12-94

---

### 4️⃣ RA: Requête Agrégation (Aggregation)

**But:** Calculer des statistiques avec count(), avg(), sum(), collect().

```cypher
-- Statistiques globales
MATCH (p:Person) WITH count(p) as person_count
MATCH (s:Skill) WITH person_count, count(s) as skill_count
MATCH (d:Document) WITH person_count, skill_count, count(d) as doc_count
RETURN person_count, skill_count, doc_count

-- Statistiques par département
MATCH (p:Person)
WITH p.department as department, 
     count(p) as person_count,
     avg(p.experience_years) as avg_experience
RETURN department, person_count, round(avg_experience * 10) / 10
ORDER BY person_count DESC
```

**Fichier:** `backend/app/routers/dashboard.py` ligne 9-54

---

### 5️⃣ RM: Requête Modification (Edit)

**But:** Créer, modifier ou supprimer des nœuds et relations.

```cypher
-- CRÉATION d'un expert
CREATE (p:Person {
    id: $id,
    name: $name,
    email: $email,
    department: $department,
    created_at: datetime()
})
RETURN p

-- MISE À JOUR d'un expert
MATCH (p:Person {id: $id})
SET p.name = $name, p.department = $department
RETURN p

-- SUPPRESSION d'un expert (avec ses relations)
MATCH (p:Person {id: $id})
DETACH DELETE p
```

**Fichier:** `backend/app/routers/experts.py` ligne 183-323

---

## 🔄 Flux de Données Complet

### Exemple: Recherche d'Experts avec Skill "Python"

```
             ┌─────────────────────────────────────────────────────────────┐
        1    │  👤 UTILISATEUR                                             │
             │     Entre "Python" dans la barre de recherche               │
             │     Sélectionne niveau ≥ 4                                  │
             └─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────────┐
        2    │  🖥️  FRONTEND (ExpertSearch.tsx)                            │
             │                                                             │
             │     const response = await expertService.search({           │
             │         skill: "Python",                                    │
             │         level: 4,                                           │
             │         limit: 20                                           │
             │     });                                                     │
             │                                                             │
             │     → Axios envoie: GET /api/experts/search?skill=Python... │
             └─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────────┐
        3    │  ⚡ BACKEND (experts.py - search_experts)                   │
             │                                                             │
             │     # Construction dynamique de la requête                  │
             │     conditions = ["p.expertise_level >= $level"]            │
             │     conditions.append("toLower(s.name) CONTAINS 'python'")  │
             │                                                             │
             │     query = '''                                             │
             │         MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)            │
             │         WHERE ''' + " AND ".join(conditions) + '''          │
             │         RETURN p.id, p.name, p.department                   │
             │     '''                                                     │
             │                                                             │
             │     result = db.run(query, params)                          │
             └─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────────┐
        4    │  🗄️  DATABASE (Neo4j)                                       │
             │                                                             │
             │     Exécution du Cypher:                                    │
             │     - Parcours des nœuds Person                             │
             │     - Suit les relations HAS_SKILL vers Skill               │
             │     - Filtre: skill.name contient "python"                  │
             │     - Filtre: person.expertise_level >= 4                   │
             │     - Trie par niveau décroissant                           │
             │     - Retourne les 20 premiers résultats                    │
             │                                                             │
             └─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────────┐
        5    │  ⚡ BACKEND                                                 │
             │                                                             │
             │     # Transformation en JSON via Pydantic                   │
             │     experts = [dict(record) for record in result]           │
             │     return experts                                          │
             │                                                             │
             │     Response (JSON):                                        │
             │     [                                                       │
             │       {"id": "exp-001", "name": "Alice", "level": 5},       │
             │       {"id": "exp-002", "name": "Bob", "level": 4}          │
             │     ]                                                       │
             └─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────────┐
        6    │  🖥️  FRONTEND                                               │
             │                                                             │
             │     setExperts(response.data);                              │
             │                                                             │
             │     Affichage dans le tableau:                              │
             │     ┌────────────────────────────────────────────────────┐  │
             │     │ Nom          │ Département  │ Niveau │ Actions    │  │
             │     ├──────────────┼──────────────┼────────┼────────────┤  │
             │     │ Alice Martin │ Engineering  │ ⭐⭐⭐⭐⭐ │ 👁️ ✏️ 🗑️ │  │
             │     │ Bob Dupont   │ Data Science │ ⭐⭐⭐⭐  │ 👁️ ✏️ 🗑️ │  │
             │     └────────────────────────────────────────────────────┘  │
             └─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Démarrage du Projet

### 1. Base de données Neo4j

```bash
# Avec Docker (recommandé)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Vérifier: http://localhost:7474
```

### 2. Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Importer les données
python scripts/import_data.py

# Lancer le serveur (port 8000)
uvicorn app.main:app --reload
```

### 3. Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement (port 5173)
npm run dev
```

### 4. Accès

| Service       | URL                        |
| ------------- | -------------------------- |
| Frontend      | http://localhost:5173      |
| API Docs      | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474      |

### 5. Identifiants par défaut

| Utilisateur | Mot de passe | Rôle          |
| ----------- | ------------ | -------------- |
| admin       | password     | Administrateur |

---

<div align="center">

---

**ExpertLink** - Université 2025/2026

*Documentation Technique Complète - Plateforme de Cartographie des Connaissances*

</div>
