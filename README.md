# ☁️ Cloud Task Manager — Dockerized Microservices

A **production-ready microservices application** built with Docker, demonstrating cloud infrastructure skills including containerization, reverse proxying, container orchestration, and CI/CD automation.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Python](https://img.shields.io/badge/Python-Flask_API-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639?style=for-the-badge&logo=nginx&logoColor=white)

---

## 🏗️ Architecture

```
┌──────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────┐
│          │      │              │      │              │      │          │
│  Client  │─────▶│    Nginx     │─────▶│  Flask API   │─────▶│  MySQL   │
│ (Browser)│ :80  │ Reverse Proxy│      │  (Gunicorn)  │ :3306│ Database │
│          │      │              │      │              │      │          │
└──────────┘      └──────────────┘      └──────────────┘      └──────────┘
                        │                      │                    │
                        └──────────────────────┴────────────────────┘
                              Docker Network (bridge)
```

### Services

| Service | Technology | Port | Purpose |
|---------|-----------|------|---------|
| **nginx** | Nginx 1.25 Alpine | 80 (exposed) | Reverse proxy, static file serving, load distribution |
| **api** | Python 3.11 + Flask + Gunicorn | 5000 (internal) | RESTful API with CRUD operations |
| **db** | MySQL 8.0 | 3306 (internal) | Persistent data storage with health checks |

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### Run the Application

```bash
# Clone the repository
git clone https://github.com/K-A-L-K-I/flask-docker-microservices.git
cd flask-docker-microservices

# Build and start all services
docker-compose up --build

# Application will be available at:
# → http://localhost
```

### Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (reset database)
docker-compose down -v
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check — returns service & DB status |
| `GET` | `/api/tasks` | Retrieve all tasks (optional `?status=pending`) |
| `GET` | `/api/tasks/:id` | Retrieve a single task by ID |
| `POST` | `/api/tasks` | Create a new task |
| `PUT` | `/api/tasks/:id` | Update an existing task |
| `DELETE` | `/api/tasks/:id` | Delete a task |
| `GET` | `/api/stats` | Get task statistics (counts by status/priority) |

### Example API Usage

```bash
# Health check
curl http://localhost/api/health

# Create a task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy to cloud", "priority": "high"}'

# Get all tasks
curl http://localhost/api/tasks

# Filter by status
curl http://localhost/api/tasks?status=pending

# Update a task
curl -X PUT http://localhost/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Delete a task
curl -X DELETE http://localhost/api/tasks/1
```

---

## 🐳 Docker Details

### Container Architecture

```
docker-compose.yml
├── db (MySQL 8.0)
│   ├── Health check: mysqladmin ping
│   ├── Persistent volume: mysql_data
│   └── Internal network only
│
├── api (Python 3.11 + Gunicorn)
│   ├── Health check: HTTP /api/health
│   ├── Depends on: db (healthy)
│   ├── 2 Gunicorn workers
│   └── Internal network only
│
└── nginx (Nginx 1.25 Alpine)
    ├── Reverse proxy → api:5000
    ├── Static files → /usr/share/nginx/html
    ├── Exposed port: 80
    └── Security headers enabled
```

### Key Docker Features Used

- **Multi-service orchestration** with Docker Compose
- **Health checks** on all services for reliability
- **Named volumes** for persistent database storage
- **Bridge network** for secure inter-container communication
- **Dependency ordering** with `depends_on` + health conditions
- **Production WSGI server** (Gunicorn instead of Flask dev server)
- **Security headers** in Nginx (X-Frame-Options, XSS Protection)
- **Docker layer caching** optimization in Dockerfile

---

## 🔄 CI/CD Pipeline

Automated with **GitHub Actions**:

```
Push to main → Lint Python → Build Docker images → Run containers → API tests → Cleanup
```

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for the full pipeline.

### Pipeline Steps:
1. **Code Quality** — Python linting with flake8
2. **Build** — Build all Docker images
3. **Deploy** — Start containers with docker-compose
4. **Test** — Run health checks and API endpoint tests
5. **Cleanup** — Tear down containers

---

## 📁 Project Structure

```
flask-docker-microservices/
│
├── app/                          # Flask API service
│   ├── app.py                    # API application (routes, DB logic)
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # API container definition
│
├── frontend/                     # Web dashboard
│   └── index.html                # Single-page dashboard (vanilla JS)
│
├── nginx/                        # Reverse proxy
│   ├── nginx.conf                # Nginx configuration
│   └── Dockerfile                # Nginx container definition
│
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD pipeline
│
├── docker-compose.yml            # Multi-container orchestration
├── .dockerignore                 # Docker build exclusions
├── .gitignore                    # Git exclusions
└── README.md                     # This file
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Containerization** | Docker + Docker Compose | Industry-standard container orchestration |
| **Reverse Proxy** | Nginx | High-performance, production-grade proxy |
| **Backend API** | Python Flask + Gunicorn | Lightweight, production WSGI deployment |
| **Database** | MySQL 8.0 | Reliable relational database with ACID compliance |
| **Frontend** | Vanilla HTML/CSS/JS | Zero dependencies, fast loading |
| **CI/CD** | GitHub Actions | Automated build, test, and deployment pipeline |

---

## 🔧 Development

```bash
# View logs for a specific service
docker-compose logs -f api

# Rebuild a single service
docker-compose build api

# Access MySQL shell
docker exec -it taskmanager-db mysql -u taskuser -ptaskpass123 taskmanager

# Check running containers
docker-compose ps

# Scale API (if needed)
docker-compose up --scale api=3
```

---

## 📜 License

This project is open source under the [MIT License](LICENSE).

---

## 👤 Author

**Nandu Anilkumar**
- 🎓 MCA Student | Saintgits College of Engineering, Kerala
- 💼 Former Intern @ CyberLabs, IIIT Kottayam
- 🔗 [LinkedIn](https://linkedin.com/in/K-A-L-K-I) | [GitHub](https://github.com/K-A-L-K-I)
