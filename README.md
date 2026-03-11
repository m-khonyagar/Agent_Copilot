# TaskFlow AI Agent

> A Personal AI Task Orchestration Platform that converts high-level goals into executable, observable workflows.

---

## Overview

TaskFlow is a self-hosted AI agent platform that lets you describe a goal in plain language and watch it get planned, executed, and tracked automatically. It combines multi-agent planning (AutoGen), reliable workflow orchestration (Temporal), sandboxed code execution (Open Interpreter), and full LLM observability (Langfuse) into a single cohesive platform.

### Key Features

- 🧠 **AI-Powered Planning** — AutoGen agents decompose complex goals into discrete, executable steps
- ⚙️ **Durable Workflow Execution** — Temporal ensures tasks survive restarts, retries failures, and scales gracefully
- 🖥️ **Sandboxed Code Execution** — Open Interpreter runs generated code safely in an isolated environment
- 📊 **Full Observability** — Langfuse traces every LLM call with latency, token usage, and cost breakdowns
- 💾 **Artifact Management** — Generated files, reports, and outputs are stored and browsable via the UI
- 🔌 **Real-time Updates** — WebSocket-powered live task status streaming to the frontend
- 🐳 **One-command Deploy** — Full stack runs via Docker Compose with a single command

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18, Tailwind CSS, Webpack | Task dashboard & real-time UI |
| Backend | FastAPI (Python 3.11), SQLAlchemy | REST API & WebSocket server |
| AI Agents | AutoGen (pyautogen) | Multi-agent planning & execution |
| Code Execution | Open Interpreter | Safe sandboxed code runner |
| Orchestration | Temporal | Durable workflow engine |
| Observability | Langfuse | LLM tracing & cost tracking |
| Database | SQLite (app) + PostgreSQL (Langfuse) | Persistence |
| Containerization | Docker, Docker Compose | Local & production deployment |

---

## Windows Quick Start

The fastest way to run TaskFlow on Windows is the included PowerShell script:

```powershell
# 1. Clone the repository
git clone https://github.com/m-khonyagar/Agent_Copilot.git
cd Agent_Copilot

# 2. Launch everything with one command
powershell -ExecutionPolicy Bypass -File taskflow\run.ps1
```

The script will:
- Verify that Docker Desktop is installed and running
- Copy `taskflow\.env.example` → `taskflow\.env` automatically if `.env` is missing (the script will pause so you can add your API keys before starting services)
- Run `docker compose up --build` inside the `taskflow` folder

Once all services are up, open your browser:

| Service | URL |
|---|---|
| Frontend UI | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| Temporal UI | http://localhost:8080 |
| Langfuse observability | http://localhost:3001 |

> **Tip:** You can also right-click `taskflow\run.ps1` in Windows Explorer and choose **"Run with PowerShell"**.

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24.0 and [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.20
- [Git](https://git-scm.com/)
- An [OpenAI API key](https://platform.openai.com/api-keys)
- (Optional) [Node.js](https://nodejs.org/) ≥ 20 and [Python](https://python.org/) ≥ 3.11 for local dev

### Clone the Repository

```bash
git clone https://github.com/m-khonyagar/Agent_Copilot.git
cd Agent_Copilot/taskflow
```

### Option A: Docker Compose (Recommended)

```bash
# 1. Copy and fill in your environment variables
cp .env.example .env
#    Edit .env and set OPENAI_API_KEY at minimum

# 2. Start the full stack
docker compose up --build

# 3. Open the apps
#    Frontend:     http://localhost:3000
#    Temporal UI:  http://localhost:8080
#    Langfuse:     http://localhost:3001
#    Backend API:  http://localhost:8000/docs
```

To stop all services:

```bash
docker compose down
# To also remove volumes (resets all data):
docker compose down -v
```

### Option B: Local Development Setup

#### Backend

```bash
cd taskflow/backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key_here
export TEMPORAL_HOST=localhost

# Run the dev server (auto-reload on save)
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd taskflow/frontend

npm install
npm start   # Starts webpack-dev-server on http://localhost:3000
```

#### Temporal (required for workflows)

```bash
# Run Temporal locally via Docker
docker run --rm -p 7233:7233 -e DB=sqlite temporalio/auto-setup:1.24.2
```

---

## Usage

1. **Open the dashboard** at [http://localhost:3000](http://localhost:3000)
2. **Enter a goal** — e.g. *"Analyze the CSV file in my workspace and generate a summary report"*
3. **Watch the plan** — The planner agent breaks it down into steps shown in the UI
4. **Monitor execution** — Steps run in real-time; outputs stream back live
5. **Review artifacts** — Download generated files from the Artifacts panel
6. **Trace LLM calls** — Visit [http://localhost:3001](http://localhost:3001) to inspect every prompt/response in Langfuse

> 📸 _Screenshots coming soon_

---

## Project Structure

```
Agent_Copilot/
├── README.md
└── taskflow/
    ├── docker-compose.yml      # Full stack orchestration
    ├── .env.example            # Environment variable template
    ├── backend/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py         # FastAPI app entry point
    │       ├── api/
    │       │   ├── tasks.py    # Task CRUD + WebSocket endpoints
    │       │   └── artifacts.py
    │       ├── agents/
    │       │   ├── planner.py  # AutoGen planner agent
    │       │   └── executor.py # Open Interpreter executor
    │       ├── workflows/
    │       │   └── task_workflow.py  # Temporal workflow definition
    │       ├── services/
    │       │   └── task_service.py
    │       └── models/
    │           └── database.py # SQLAlchemy models
    └── frontend/
        ├── Dockerfile
        ├── package.json
        ├── webpack.config.js
        └── src/
            ├── index.js
            ├── App.jsx
            ├── api.js          # Axios client
            ├── components/     # Shared UI components
            └── pages/          # Route-level page components
```

---

## Configuration

All configuration is via environment variables. Copy `taskflow/.env.example` to `taskflow/.env` and edit it.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ | — | OpenAI API key for LLM calls |
| `TEMPORAL_HOST` | ❌ | `temporal` | Hostname of the Temporal frontend service |
| `LANGFUSE_HOST` | ❌ | `http://langfuse:3000` | Internal Langfuse server URL |
| `LANGFUSE_PUBLIC_KEY` | ❌ | — | Langfuse project public key (for tracing) |
| `LANGFUSE_SECRET_KEY` | ❌ | — | Langfuse project secret key (for tracing) |
| `LANGFUSE_POSTGRES_DB` | ❌ | `langfuse` | Langfuse PostgreSQL database name |
| `LANGFUSE_POSTGRES_USER` | ❌ | `langfuse` | Langfuse PostgreSQL username |
| `LANGFUSE_POSTGRES_PASSWORD` | ❌ | `langfuse` | Langfuse PostgreSQL password — **change in production** |
| `LANGFUSE_NEXTAUTH_SECRET` | ❌ | `supersecret` | Langfuse session secret — **change in production** |
| `LANGFUSE_SALT` | ❌ | `supersalt` | Langfuse password hash salt — **change in production** |

> **Note:** Langfuse tracing is optional. The platform operates fully without it — traces are simply not recorded.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User Browser                      │
│              React Frontend  :3000                   │
└───────────────────┬─────────────────────────────────┘
                    │  REST + WebSocket
                    ▼
┌─────────────────────────────────────────────────────┐
│               FastAPI Backend  :8000                 │
│                                                      │
│  ┌─────────────┐   ┌──────────────────────────────┐ │
│  │  AutoGen    │   │    Temporal Workflow Client   │ │
│  │  Planner    │──▶│    (schedules & monitors)     │ │
│  └─────────────┘   └──────────────┬───────────────┘ │
│                                   │                  │
│  ┌─────────────────────────────┐  │                  │
│  │  Langfuse SDK  (tracing)    │  │                  │
│  └─────────────────────────────┘  │                  │
└───────────────────────────────────┼─────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │    Temporal Server  :7233        │
                    │  (durable workflow execution)    │
                    │                                  │
                    │  ┌───────────────────────────┐  │
                    │  │  Task Workflow Worker      │  │
                    │  │  └─ Open Interpreter       │  │
                    │  │     (sandboxed code exec)  │  │
                    │  └───────────────────────────┘  │
                    └────────────────────────────────┘
                                    │
              ┌─────────────────────┴──────────────────┐
              │                                         │
┌─────────────▼───────────┐         ┌──────────────────▼────┐
│  SQLite  (app data)     │         │  Langfuse  :3001       │
│  tasks, artifacts, logs │         │  + PostgreSQL  :5432   │
└─────────────────────────┘         └───────────────────────┘
```

---

## Development Notes

- **Hot reload:** The backend uses `uvicorn --reload`; the frontend uses `webpack-dev-server --hot`. Both are active in local dev mode.
- **Temporal UI** at [http://localhost:8080](http://localhost:8080) lets you inspect workflow runs, activity histories, and retry state.
- **API docs** (Swagger UI) are auto-generated at [http://localhost:8000/docs](http://localhost:8000/docs).
- **Database migrations:** SQLAlchemy creates tables on startup via `Base.metadata.create_all()`. For production, migrate to Alembic.
- **Secrets:** Never commit your `.env` file. It is listed in `.gitignore` by convention; verify before pushing.
- **Scaling workers:** To run additional Temporal workers, duplicate the `backend` service in `docker-compose.yml` with a different name and no exposed ports.