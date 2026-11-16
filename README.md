# README

## Project setup

- This solution uses [uv](https://docs.astral.sh/uv/) as the Python and package manager.

- This solution uses [just](https://just.systems/man/en/) for running CLI commands. There are three `.justfile`s: one in the project root and one for each service.

  The complete application can be started with:

```bash
just up
```

This command starts both the tools and agent services.

The agent can then be queried via:

```bash
just curl
```

This sends the following query to the agent:

> "What is the latest news on batteries? And is there positive sentiment around this news?"

You can also pass a custom query by appending it to the command:

```bash
just curl "your query"
```

- This solution uses [Ruff](https://docs.astral.sh/ruff/) for linting, import sorting, and formatting, and [Pyright](https://github.com/microsoft/pyright) for static type checking.

- This solution uses [GitHub Models](https://github.com/marketplace/models). The agent connects to the model via the [GitHubProvider](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.github.GitHubProvider) class from [Pydantic AI](https://pydantic.dev/docs/ai/models/overview/).

  If you would like to test the solution with a different provider, you may need to modify the provider class in:

```text
services/research_agent/research_agent/clients.py
```

specifically inside the `create_model_client` function.

## Components

### 1. Research tools (MCP Server)

- built with FastMCP
- exposes three tools: `search`, `synthesize`, and `analyze`
- the `analyze` tool performs analysis via [MCP Sampling](https://gofastmcp.com/servers/sampling)
- uses `LoggingMiddleware` to propagate selected logs to the MCP client/agent
- uses `ErrorHandlingMiddleware` to prevent the server from crashing during failures, reducing the need for repetitive `try/except` blocks

### 2. Research agent

- built with Pydantic AI and FastAPI
- connects to the MCP server via the streamable HTTP transport
- uses the new [MCPToolset](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) class from Pydantic AI, which is now the recommended approach

  However, `MCPToolset` does not yet support MCP Sampling natively, so I implemented a custom `SamplingHandler` for this functionality.

  In contrast, the now-deprecated [MCPServer](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPServer) class supported this functionality out of the box.

- uses a custom log handler to receive logs propagated from the MCP server

## Limitations

- I spent limited time on testing, so the current test coverage is intentionally minimal. However, I consider testing to be an important part of production-grade systems.
- I unfortunately did not manage to spend time on evals. In particular, I wanted to experiment with the new [Pydantic Evals](https://pydantic.dev/docs/ai/evals/evals/) library.
- The current search engine implementation is intentionally simple, which impacts retrieval quality, especially when using smaller or less capable models.
- I did not spend significant time optimizing concurrency, throughput, or latency characteristics, as I prioritized correctness, architecture, and maintainability for the scope of the assignment.

## Future improvement ideas

- Improve the search capabilities of the search tool (e.g. semantic similarity search, embeddings, or RAG-based retrieval).
- Increase test coverage, including edge cases and failure scenarios.
- Add evaluation pipelines, including LLM-as-a-judge evaluations.
- Add observability and tracing for agent/tool interactions.
- Add caching for repeated or semantically similar queries.
- Add retry and fallback strategies across MCP tools and model calls.