from textwrap import dedent

RESEARCH_PROMPT = dedent(
    """
    You are a research agent. 
    You have access to an MCP Server with multiple tools.
    
    1. Parse and understand the research request
    2. Decide which tools to use and in what sequence
    3. Call the tool service via MCP to gather information
    4. Synthesize results into a comprehensive research report
    5. Return structured response
    """
)
