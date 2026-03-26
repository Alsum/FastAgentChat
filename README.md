# FastAgentChat - AI Agent Platform Backend

FastAgentChat is a professionally architected backend service for a next-generation AI Agent Platform. It enables developers and users to build, manage, and interact with specialized AI agents through both text and voice interfaces.

## 🚀 Architecture Overview

The system is built on a modular, asynchronous architecture using **FastAPI** and **SQLAlchemy 2.0**. This design ensures high performance, maintainability, and scalability.

### Technical Design Components:
1.  **FastAPI (Web Framework)**: High-performance, asynchronous web framework leveraging standard Python type hints for effortless data validation and documentation.
2.  **SQLAlchemy (ORM)**: Advanced ORM utilizing the latest 2.0 syntax, with a clean separation between database models and API schemas.
3.  **Alembic (Migration System)**: Version control for the database schema, allowing for seamless structural updates.
4.  **OpenAI Integration**: Deep integration with cutting-edge AI models:
    *   **GPT-4o**: For intelligent, context-aware conversations.
    *   **Whisper (STT)**: For high-fidelity speech-to-text transcription.
    *   **OpenAI TTS**: For natural-sounding text-to-speech generation.
5.  **Pydantic (Data Validation)**: Robust schema validation for incoming and outgoing data, ensuring system stability.

---

## 🏗️ Technical Implementation Analysis

### 1. Database Schema
The database is structured to support complex agent configurations and conversation tracking:
- **Agents**: Stores agent identities, custom system prompts, and voice profiles.
- **Conversations**: Manages session history (extensible for multi-user chat).
- **Messages**: Maintains a full audit log of interactions (text and audio).

### 2. Service Layer Pattern
Logic for third-party API interactions is isolated in the `services/` directory. This decouples the AI implementation from the API delivery layer, allowing for easy transitions between different AI providers in the future.

### 3. File System & Media Handling
- **Async File Streams**: Uses `aiofiles` and FastAPI's `UploadFile` for non-blocking file handling.
- **Static Asset Serving**: Automatically mounts a `media/` directory for hosting generated voice assets.

### 4. Quality Assurance
- **Automated Testing**: Comprehensive test suite using `pytest` and `httpx`.
- **OpenAI Mocking**: Tests are designed to run independently of the OpenAI API using mock objects, ensuring stable CI/CD pipelines.

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API Key

### Installation
1.  Navigate to the project root.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ensure your `.env` contains:
    ```env
    DATABASE_URL=sqlite:///./fast_agent_chat.db
    OPENAI_API_KEY=sk-...
    ```

### Running the Platform
Launch the development server:
```bash
uvicorn app.main:app --reload
```
Documentation is auto-generated at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📡 API Reference

### Agent Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/agents/` | Register a new AI Agent with a custom prompt. |
| `GET` | `/agents/` | List all registered agents. |
| `GET` | `/agents/{id}` | Retrieve detailed agent configuration. |
| `PATCH` | `/agents/{id}` | Update agent name, prompt, or voice. |
| `DELETE` | `/agents/{id}` | Remove an agent from the platform. |

### AI Interaction
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/agents/{id}/chat` | Text-based conversation. Returns AI text and optional TTS audio. |
| `POST` | `/agents/{id}/voice-chat` | Voice-to-voice interaction. Upload audio, get audio response back. |

---

## 🛡️ Best Practices Implemented
- **Modular Project Structure**: Clean separation of models, schemas, routers, and services.
- **Environment Management**: Secure configuration using `.env` files and `pydantic-settings`.
- **Database Migrations**: Integrated Alembic for structural versioning.
- **Scalable Media Support**: Dedicated static file serving for AI voice responses.
- **Async Everywhere**: Leverages Python's `async/await` for optimal I/O performance.
