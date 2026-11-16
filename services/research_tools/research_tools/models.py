from pydantic import BaseModel, Field, model_validator


class ExtractKeywordParameters(BaseModel):
    user_query: str = Field(
        description="Original user query used to extract the primary keyword from"
    )


class SearchParameters(BaseModel):
    keyword: str = Field(
        description="Primary search keyword derived from the user input"
    )
    sources: list[str] | None = Field(description="Preferred sources to search within")
    max_results: int = Field(description="Maximum number of results to return")


class SearchOutput(BaseModel):
    search_output: list[str] | None = Field(
        description="Search results returned by the search tool"
    )
    found_results: bool = Field(
        description="Whether the search returned matching results"
    )

    @model_validator(mode="after")
    def validate_consistency(self):
        if not self.found_results and self.search_output is not None:
            raise ValueError("search_output must be None when found_results=False")

        if self.found_results and not self.search_output:
            raise ValueError("search_output is required when found_results=True")

        return self


class SynthesizeParameters(BaseModel):
    search_output: list[str] = Field(description="Search results to synthesize")


class SynthesizeOutput(BaseModel):
    synthesize_output: str = Field(
        description="Synthesized representation of the search results"
    )


class AnalyzeParameters(BaseModel):
    synthesize_output: str = Field(description="Synthesized content to analyze")
    user_query: str = Field(
        description="Original user query used to guide the analysis"
    )
