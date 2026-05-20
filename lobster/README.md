# AI Engineer Assessment - Research Agent

Build an intelligent research agent using LLM + tools.

**Time: 3 hours**

## Task

Implement a research agent that:
1. Takes natural language research requests 
2. Uses tools to search, synthesize, and analyze information
3. Returns comprehensive research reports

## What to Build

**Research Agent Service** (Port 8000):
- `/research` endpoint accepting natural language queries
- Uses LLM to orchestrate tool calls intelligently
- Integrates with research tools via MCP protocol

**Research Tools Service** (Port 8001): 
- MCP-compliant tools: `search`, `synthesize`, `analyze`
- Uses provided mock data in `/data` folder
- Simple keyword/text search is acceptable (no semantic search required)
- Returns structured research results

## Key Technologies

- **Python 3.12+**
- **FastAPI** for API framework
- **Pydantic** for data validation
- **Your choice of AI/ML libraries** (OpenAI, Anthropic, local models, etc.)
- **Docker** (optional)

## Key Requirements

- Use any LLM provider (OpenAI, Anthropic, etc.)
- Implement MCP protocol for tool communication (tip: read up on MCP)
- Focus on intelligent tool orchestration
- Handle errors gracefully

## Agent Workflow

The agent should follow this research pattern:
1. **Search** for relevant sources on the topic
2. **Synthesize** findings from multiple sources  
3. **Analyze** synthesized content for insights
4. Return comprehensive research report

## Getting Started

1. Examine `starter_code/` structure
2. Review mock data in `data/` folder  
3. Implement both services
4. Test with: `curl -X POST http://localhost:8000/research -d '{"query": "What is the latest news on batteries? And is there a positive sentiment to these news?"}'`