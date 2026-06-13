# HafteYar (هفته‌یار) 🤖📅

**HafteYar** is an AI-First, Bot-First project and team management platform. It allows users and teams to manage their workflows, tasks, and weekly planning entirely through natural language conversations on messaging platforms like Telegram and Bale, backed by a robust AI middleware.

## Core Philosophy

* **AI-First & Bot-First**: The primary user journey is through conversation bots (Telegram / Bale) interacting with our AI Middleware, not traditional Web UIs.
* **Hybrid Architecture**: Users can interact via traditional direct API actions (buttons) or choose the Premium AI Path for natural language requests using advanced LLMs via **Gapgpt**.
* **Human-in-the-Loop Execution**: All AI-proposed actions (Execution Plans) require explicit confirmation (Green/Yellow/Red statuses) before execution, ensuring safety and precision.

## Architecture

* **Domain-Driven Design (DDD)**: Clean architecture separating Domain, Application, and Infrastructure layers.
* **AI Middleware Layer**: Handles Conversation Management, Context Tracking (Team/Project/User), Intent Detection, and Tool Execution.
* **Subscription Gating**: Deep integration of features like `AI_CHAT`. Advanced capabilities are strictly gated based on team subscription plans.
* **Technology Stack**: Python, FastAPI, SQLAlchemy, SQLite (Development) / PostgreSQL (Production), Alembic for migrations.

## Key Features

* **Multi-Modal Conversations**: Supports parsing and context tracking for Text, Voice, and Image messages.
* **Execution Plan Snapshots**: AI context is snapshotted upon plan generation to guarantee deterministic execution, regardless of real-time state changes.
* **Team & Project Contexts**: Seamlessly switch between active teams and projects natively inside the conversation.
* **Custom AI Execution Modes**: Configurable settings per team (`ALWAYS_REVIEW`, `REVIEW_CRITICAL_ONLY`, `AUTO_EXECUTE`).

## Getting Started (Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/abumahdiii/HafteYar2.git
   cd HafteYar2
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the FastAPI server (coming soon via Uvicorn):
   ```bash
   # uvicorn src.infrastructure.entrypoints.api.v1.app:app --reload
   ```

## License
Proprietary / Closed Source. All rights reserved.
