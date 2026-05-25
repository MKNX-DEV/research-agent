from pydantic import BaseModel, Field


class SearchParameters(BaseModel):
    keyword: str = Field(
        description="Primary search keyword derived from the user input"
    )
    sources: list[str] | None = Field(description="Sources to search within")
    max_results: int = Field(description="Maximum number of results to return")


class SearchOutput(BaseModel):
    search_output: list[str] | None = Field(description="Search results returned")


class SynthesizeParameters(BaseModel):
    search_output: list[str] = Field(description="Search results to synthesize")


class SynthesizeOutput(BaseModel):
    synthesize_output: str = Field(description="Synthesized search results")


class AnalyzeParameters(BaseModel):
    synthesize_output: str = Field(description="Synthesized search results to analyze")
    user_query: str = Field(
        description="User original query to use to analyze the synthesized content against"
    )
