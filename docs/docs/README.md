# Netflix KDD System

A small service-based system for exploring the Netflix Titles dataset with MongoDB Atlas.
Built for **Assignment 1 — Data at Rest**.

---

## Architecture

```
                         ┌─────────────────────────┐
                         │      Nginx gateway      │
                         │        :8080            │
                         └────────────┬────────────┘
                                      │
                     /api/*           │           /analysis/*
        ┌─────────────────────────────┴─────────────────────────────┐
        ▼                                                           ▼
┌───────────────────┐                                     ┌────────────────────┐
│   api-service     │                                     │  analysis-service  │
│   FastAPI :8001   │                                     │  FastAPI :8002     │
│   CRUD + search   │                                     │  4 KDD aggregations│
└─────────┬─────────┘                                     └──────────┬─────────┘
          │                                                          │
          └──────────────────────────┬───────────────────────────────┘
                                     ▼
                     MongoDB Atlas — cluster: TestCluster
                     database: assignment1
                     collection: records  (8,807 documents)
```

Two FastAPI services, each with a distinct responsibility, sit behind an Nginx gateway.
Both connect to the same MongoDB Atlas cluster using credentials read from the environment.

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11 or 3.12 | one-off import script + local dev |
| Docker Desktop | 24+ | run the containerised stack |
| MongoDB Atlas account | free tier | data store (external) |

A connection string is required — see `.env.example`.

---

## Repository layout

```
netflix-kdd-system/
├── data/
│   └── netflix_titles.csv         # source dataset (8,807 rows)
├── scripts/
│   └── import_data.py             # one-off loader: CSV → MongoDB
├── api-service/                   # Service A — records API
│   ├── app/main.py
│   ├── app/db.py
│   ├── app/routes.py
│   ├── requirements.txt
│   └── Dockerfile
├── analysis-service/              # Service B — KDD aggregations
│   ├── app/main.py
│   ├── app/db.py
│   ├── app/pipelines.py
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/
│   └── nginx.conf                 # gateway routing
├── k8s/                           # Kubernetes manifests
├── docs/
│   ├── findings.md
│   └── screenshots/
├── .env                           # secrets — NOT committed
├── .env.example                   # template
├── .gitignore
└── docker-compose.yml
```

---

## Setup (once)

### 1. Clone and enter the project

```powershell
git clone <your-repo-url> netflix-kdd-system
cd netflix-kdd-system
```

### 2. Create `.env`

Copy the template and fill in your Atlas credentials:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```env
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DB_NAME=assignment1
COLLECTION=records
```

> **Note**: If the password contains `@ : / ? # & %`, URL-encode them
> (`@` → `%40`, `:` → `%3A`, `/` → `%2F`, `?` → `%3F`, `#` → `%23`, `&` → `%26`, `%` → `%25`).

### 3. Whitelist your IP in Atlas

Atlas → **Network Access** → **Add Current IP Address**.

### 4. Install Python dependencies for the loader

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install pymongo python-dotenv
```

### 5. Load the dataset into MongoDB

```powershell
python scripts/import_data.py
```

Expected output:

```
Reading C:\...\data\netflix_titles.csv
8807 records ready for insert
Inserted 8807 documents into assignment1.records
Indexes created: release_year, type, director
```

---

## Running the system

### Option A — Docker Compose (recommended)

```powershell
docker compose up --build
```

First build takes 2–5 minutes. When done, three containers should be running:

| Container | Port | Role |
|---|---|---|
| `netflix-api` | 8001 | records API |
| `netflix-analysis` | 8002 | analysis service |
| `netflix-gateway` | **8080** | public entry point |

Test:

```powershell
curl.exe http://localhost:8080
curl.exe "http://localhost:8080/api/titles?limit=5"
curl.exe "http://localhost:8080/analysis/genres"
```

Or open in a browser:

| URL | What it returns |
|---|---|
| http://localhost:8080/ | Gateway status message |
| http://localhost:8080/api/titles?limit=5 | 5 records |
| http://localhost:8080/api/titles/search?q=dark | search results |
| http://localhost:8080/analysis/genres | **Q1** top genres |
| http://localhost:8080/analysis/ratings-by-type | **Q2** rating split |
| http://localhost:8080/analysis/top-directors | **Q3** top directors |
| http://localhost:8080/analysis/release-years | **Q4** year distribution |
| http://localhost:8001/docs | API service Swagger UI |
| http://localhost:8002/docs | Analysis service Swagger UI |

To stop:

```powershell
docker compose down
```

### Option B — Kubernetes (Docker Desktop)

Prerequisites: **Docker Desktop → Kubernetes → Enable** (uses kind, single node).

```powershell
# 1. Build images with names the manifests expect
docker build -t netflix-api:latest      ./api-service
docker build -t netflix-analysis:latest ./analysis-service

# 2. Put the real URI into k8s/secret.yaml (never commit it)

# 3. Apply manifests
kubectl apply -f k8s/

# 4. Wait for pods
kubectl get pods -n netflix-kdd
```

Expected: 5 pods running (2× api-service, 2× analysis-service, 1× nginx).

Expose locally via port-forward:

```powershell
kubectl port-forward -n netflix-kdd svc/nginx 8081:80
```

Then browse to `http://localhost:8081/analysis/genres`.

Tear down:

```powershell
kubectl delete namespace netflix-kdd
```

---

## API reference

### API service (`/api/*`)

| Method | Path | Description |
|---|---|---|
| GET | `/api/titles` | List records. Query params: `limit`, `skip`, `type` |
| GET | `/api/titles/search?q=` | Case-insensitive search over `title`, `director`, `cast` |
| GET | `/api/titles/{id}` | Fetch one record by ObjectId |
| DELETE | `/api/titles/{id}` | Delete a record |
| GET | `/health` | Health check |

### Analysis service (`/analysis/*`)

| Method | Path | KDD question |
|---|---|---|
| GET | `/analysis/genres` | Which genres have the most titles? |
| GET | `/analysis/ratings-by-type` | Maturity rating split per content type |
| GET | `/analysis/top-directors` | Which directors appear most often? |
| GET | `/analysis/release-years` | Distribution of release years |
| GET | `/health` | Health check |

---

## Configuration and secrets

| Config | Where it lives | Notes |
|---|---|---|
| Atlas URI | `.env` (local) / `k8s/secret.yaml` (K8s) | git-ignored; injected via `env_file` in Compose, `envFrom.secretRef` in K8s |
| DB name, collection | `.env` / `k8s/configmap.yaml` | not sensitive |
| Nginx config | `nginx/nginx.conf` | bind-mounted read-only |

> **Never** commit `.env` or a `secret.yaml` that contains a real URI.
> In production, create the K8s secret imperatively:
>
> ```powershell
> kubectl create secret generic mongo-secret -n netflix-kdd `
>   --from-literal=MONGO_URI="mongodb+srv://..."
> ```

---

## KDD questions answered

1. **Which genres have the most titles?** → `$split` + `$unwind` on `listed_in`
2. **Maturity rating distribution per content type** → `$group` on composite key `{rating, type}`
3. **Which directors appear most often?** → `$match` + `$group` on `director`, nulls excluded
4. **Distribution of release years** → `$group` + `$sort` on `release_year`

See `docs/findings.md` for the actual results and `analysis-service/app/pipelines.py`
for the aggregation definitions.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ServerSelectionTimeoutError` | Your IP isn't whitelisted in Atlas, or the password is wrong |
| `authentication failed` | Password in `.env` doesn't match Atlas. Reset in **Database Access** |
| Nginx container exits with `unknown directive` | `nginx.conf` was saved with a BOM. Re-save as UTF-8 without BOM |
| `kubectl` can't find images | `docker build` the images with the same names as in `k8s/*.yaml` |
| Nginx pod crashes with `host not found in upstream` | Restart the pod after api/analysis pods are Ready: `kubectl delete pod -n netflix-kdd -l app=nginx` |

---

## License / attribution

Dataset: Netflix Movies and TV Shows — Kaggle (`shivamb/netflix-shows`), CC0 Public Domain.
Assignment project, 2026.