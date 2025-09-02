# 🎮 NPC Game Backend

<div align="center">
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
  [![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
  [![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
  [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

  **A modern, high-performance FastAPI backend service for NPC (Non-Player Character) game interactions**

  [📚 API Docs](http://localhost:8000/docs) • [🔧 Configuration](#-configuration) • [🚀 Quick Start](#-quick-start) • [🤝 Contributing](#-contributing)

</div>

---

## ✨ Features

<table>
<tr>
<td>

🚀 **High Performance**
- FastAPI async framework
- Optimized database queries
- Redis caching layer

</td>
<td>

🔐 **Security First**
- JWT-based authentication
- Password hashing with Passlib
- Session management

</td>
</tr>
<tr>
<td>

🎮 **Game Systems**
- NPC management & interactions
- Session handling & state
- User progress tracking

</td>
<td>

🛠️ **Developer Experience**
- Auto-generated API docs
- Database migrations
- Docker containerization

</td>
</tr>
</table>

## 🏗️ Architecture

```mermaid
graph TB
    A[Client] -->|HTTP Requests| B[FastAPI Backend]
    B --> C[Authentication Service]
    B --> D[NPC Service]
    B --> E[Session Service]
    B --> F[User Service]
    
    C --> G[(PostgreSQL)]
    D --> G
    E --> G
    F --> G
    
    B --> H[(Redis Cache)]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style G fill:#e8f5e8
    style H fill:#fff3e0
```

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/-Python%203.11+-3776ab?style=flat&logo=python&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL%2015-336791?style=flat&logo=postgresql&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy%202.0-red?style=flat) |
| **Cache** | ![Redis](https://img.shields.io/badge/-Redis%207-dc382d?style=flat&logo=redis&logoColor=white) |
| **Auth** | ![JWT](https://img.shields.io/badge/-JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white) ![Passlib](https://img.shields.io/badge/-Passlib-green?style=flat) |
| **DevOps** | ![Docker](https://img.shields.io/badge/-Docker-2496ed?style=flat&logo=docker&logoColor=white) ![Alembic](https://img.shields.io/badge/-Alembic-orange?style=flat) |
| **Tools** | ![Poetry](https://img.shields.io/badge/-Poetry-60a5fa?style=flat&logo=poetry&logoColor=white) |

## 📋 Prerequisites

> **Note**: Make sure you have the following installed on your system:

- 🐍 **Python 3.11+**
- 📦 **Poetry** (dependency management)
- 🐳 **Docker & Docker Compose**
- 🐘 **PostgreSQL 15** (for local development)
- 🔴 **Redis 7** (for local development)

## 🚀 Quick Start

### 🐳 Docker Setup (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai_agent_backend

# 2. Environment setup
cp .env.example .env
# Edit .env with your configuration

# 3. Launch all services
docker-compose up -d

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. 🎉 You're ready to go!
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 🔧 Local Development

<details>
<summary>Click to expand local development setup</summary>

```bash
# 1. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Install dependencies
poetry install

# 3. Activate virtual environment
poetry shell

# 4. Setup environment
cp .env.example .env

# 5. Start databases
docker-compose up -d db redis

# 6. Run migrations
alembic upgrade head

# 7. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

</details>

## 📁 Project Structure

```
ai_agent_backend/
├── 📁 alembic/              # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── 📁 app/
│   ├── 📁 api/              # 🛣️ API route handlers
│   │   ├── npc.py
│   │   ├── sessions.py
│   │   └── users.py
│   ├── 📁 core/             # ⚙️ Core configuration
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── redis.py
│   │   └── security.py
│   ├── 📁 models/           # 🗃️ SQLAlchemy models
│   │   ├── npc.py
│   │   ├── session.py
│   │   └── user.py
│   ├── 📁 repositories/     # 💾 Data access layer
│   │   ├── npc_repo.py
│   │   ├── session_repo.py
│   │   └── user_repo.py
│   ├── 📁 schemas/          # 📋 Pydantic schemas
│   │   ├── npc.py
│   │   ├── session.py
│   │   └── user.py
│   ├── 📁 services/         # 🧠 Business logic
│   │   ├── npc_service.py
│   │   ├── session_service.py
│   │   └── user_service.py
│   └── 📄 main.py           # 🚀 FastAPI application
├── 🐳 docker-compose.yml
├── 📦 pyproject.toml
└── 📖 README.md
```

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# 🗄️ Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5434/npc_game

# 🔴 Redis Configuration
REDIS_URL=redis://localhost:6380

# 🔐 Security Settings
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 🌍 Environment Settings
ENVIRONMENT=development
DEBUG=true
```

## 📚 API Documentation

Once the server is running, explore the API:

| Service | URL | Description |
|---------|-----|-------------|
| 🏠 **Home** | http://localhost:8000 | Health check endpoint |
| 📖 **Swagger UI** | http://localhost:8000/docs | Interactive API documentation |
| 📚 **ReDoc** | http://localhost:8000/redoc | Alternative API documentation |

### 🛣️ Key Endpoints

<details>
<summary>👥 User Management</summary>

- `POST /users/register` - Register new user
- `POST /users/login` - User authentication
- `GET /users/me` - Get current user profile

</details>

<details>
<summary>🎮 Session Management</summary>

- `POST /sessions/` - Create new game session
- `GET /sessions/` - List user sessions
- `GET /sessions/{id}` - Get session details

</details>

<details>
<summary>🤖 NPC Management</summary>

- `POST /npc/` - Create new NPC
- `GET /npc/` - List all NPCs
- `GET /npc/{id}` - Get NPC details

</details>

## 🗄️ Database Operations

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## 🧪 Development & Testing

```bash
# Install development dependencies
poetry install --with dev

# Run tests
pytest

# Code formatting
black .
isort .
flake8 .
```

## 🐳 Docker Commands

```bash
# 🚀 Start all services
docker-compose up -d

# 📋 View logs
docker-compose logs -f backend

# 🛑 Stop services
docker-compose down

# 🔄 Rebuild and restart
docker-compose up -d --build

# 💻 Access backend container
docker-compose exec backend bash
```

## 🔮 Roadmap

- [ ] 🌐 WebSocket support for real-time interactions
- [ ] 🧠 Advanced NPC AI behaviors using LLMs
- [ ] 💾 Enhanced game state persistence
- [ ] 👥 Multiplayer session support
- [ ] 📊 Performance monitoring and metrics
- [ ] 🚦 API rate limiting
- [ ] 🧪 Comprehensive test coverage
- [ ] 🎨 Admin dashboard
- [ ] 📱 Mobile API optimizations

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. ✅ Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔃 Open a Pull Request

### 📝 Contribution Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Use conventional commit messages

## 🆘 Support

Need help? We're here for you!

- 🐛 [Create an Issue](https://github.com/your-username/ai_agent_backend/issues)
- 💬 [Discussions](https://github.com/your-username/ai_agent_backend/discussions)
- 📧 Contact the maintainer

## 👨‍💻 Author

**Amin Soltobekov**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/amin-soltobekov-482b5430b/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  
  **⭐ Star this repo if you find it helpful!**
  
  Made with ❤️ and ☕ by [Amin Soltobekov](https://www.linkedin.com/in/amin-soltobekov-482b5430b/)

</div>