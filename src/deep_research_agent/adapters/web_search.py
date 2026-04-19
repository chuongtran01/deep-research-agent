
import os
from typing import List, Type, Annotated, Literal, Union

from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

load_dotenv()


class SearchResult(BaseModel):
    title: Annotated[str, Field(description="The title of the result")]
    url: Annotated[str, Field(description="The URL of the result")]
    content: Annotated[str, Field(description="The content of the result")]
    score: Annotated[float, Field(description="The score of the result")]
    raw_content: Annotated[Union[str, None], Field(
        description="The raw content of the result")]


class SearchToolArgs(BaseModel):
    query: Annotated[str, Field(description="The query to search for")]
    max_results: Annotated[int, Field(
        description="The maximum number of results to return", default=5, ge=1, le=100)]
    include_raw_content: Annotated[bool, Field(
        description="Whether to include the raw content of the results", default=False)]
    search_depth: Annotated[Literal["basic", "advanced", "fast", "ultra-fast"], Field(
        description="The depth of the search", default="basic")]


class SearchTool(BaseTool):
    name: str = "search_tool"
    description: str = "Search the web for information"
    args_schema: Type[BaseModel] = SearchToolArgs

    _api_key: str = PrivateAttr()
    _client: TavilyClient = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("TAVILY_API_KEY")
        if not self._api_key:
            raise ValueError("TAVILY_API_KEY is not set")

        self._client = TavilyClient(api_key=self._api_key)

    def search(
        self,
        query: str,
        max_results: int = 5,
        include_raw_content: bool = False,
        search_depth: Literal["basic", "advanced",
                              "fast", "ultra-fast"] = "basic",
    ) -> List[SearchResult]:
        # Validate search depth
        valid_search_depths = ["basic", "advanced", "fast", "ultra-fast"]
        if search_depth not in valid_search_depths:
            raise ValueError(
                f"Invalid search depth: {search_depth}. Valid search depths are: {valid_search_depths}")

        # Search the web
        response = self._client.search(
            query=query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            search_depth=search_depth,
        )

        return [SearchResult(**r) for r in response["results"]]

    def _run(self, query: str,
             max_results: int = 5,
             include_raw_content: bool = False,
             search_depth: Literal["basic", "advanced",
                                   "fast", "ultra-fast"] = "basic"
             ) -> List[SearchResult]:
        return self.search(query=query, max_results=max_results, include_raw_content=include_raw_content, search_depth=search_depth)
