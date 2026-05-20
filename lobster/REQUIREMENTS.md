# Technical Requirements

## Required Services

**Research Tools Service (Port 8001):**
- MCP-compliant service implementing research tools
- Use provided mock data sources
- Test MCP implementation with proper MCP clients

**Research Agent Service (Port 8000):**
- `POST /research` - Accept natural language research queries
- `GET /` - Health check

## MCP Tools to Implement

**search**
- Purpose: Search for information in mock data sources
- Parameters: 
  - `sources` (string): Knowledge base category to filter search
  - `query` (string): Search query keyword
  - `max_results` (int): Maximum number of results to return

**synthesize**
- Purpose: Combine multiple sources into coherent summary
- Parameters:
  - `source_contents` (list of strings): Source texts to synthesize
- Returns: Synthesized text with inline citations

**analyze**
- Purpose: Analyze synthesized content for insights
- Parameters:
  - `synthesized_content` (string): The synthesized text to analyze
  - `user_query` (string): User query for analysis focus
- Returns: Analysis results based on user query

## Agent Requirements

- Parse natural language research requests
- Decide which tools to use in what sequence
- Generate appropriate parameters for tool calls
- Synthesize comprehensive research reports
- Handle errors gracefully

## Testing

Test the agent endpoint:
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the latest news on batteries? And is there a positive sentiment to these news?"}'
```