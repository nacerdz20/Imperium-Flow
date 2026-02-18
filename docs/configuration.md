# Configuration

Imperium Flow uses environment variables for configuration. You can create a `.env` file in the root directory.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CONDUCTOR_SERVER_URL` | URL of the Conductor server API | `http://localhost:8080/api` |
| `LOG_LEVEL` | Python logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MEMORY_PATH` | Path to the local JSON memory store | `.imperium/memory.json` |
| `MAX_RETRIES` | Default retry count for agent tasks | `3` |
| `DASHBOARD_PORT` | Port for the FastAPI dashboard | `8090` |

## LLM Configuration (Optional)

If integrated with real LLMs (OpenAI, Anthropic):

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Key for GPT-4/3.5 models |
| `ANTHROPIC_API_KEY` | Key for Claude models |

## Logging

Logs are written to standard output by default. You can configure file logging by modifying the `structlog` configuration in `src/core/config.py`.
