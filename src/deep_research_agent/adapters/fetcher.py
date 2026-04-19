from langchain_core.tools import BaseTool
from pydantic import BaseModel, PrivateAttr
import requests
from bs4 import BeautifulSoup
from typing import Type


class FetcherResult(BaseModel):
    url: str
    status_code: int | None
    content_type: str | None
    content_length: int | None
    text: str | None
    error: str | None


class FetcherArgs(BaseModel):
    url: str


class Fetcher(BaseTool):
    name: str = "fetcher"
    description: str = "Fetch the content of a URL"
    args_schema: Type[BaseModel] = FetcherArgs

    _timeout: int = PrivateAttr()
    _headers: dict[str, str] = PrivateAttr()

    def __init__(self, timeout: int = 10):
        super().__init__()

        self._timeout = timeout
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def _run(self, url: str) -> FetcherResult:
        return self.fetch(url)

    def fetch(self, url: str) -> FetcherResult:
        try:
            response = requests.get(
                url, headers=self._headers, timeout=self._timeout)
            response.raise_for_status()

            html = response.text
            text = self._extract_text(html)

            return FetcherResult(
                url=url,
                status_code=response.status_code,
                content_type=response.headers.get("Content-Type", ""),
                content_length=len(response.content),
                text=text,
                error=None,
            )

        except requests.RequestException as e:
            return FetcherResult(
                url=url,
                status_code=None,
                content_length=None,
                content_type=None,
                text=None,
                error=str(e),
            )

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]

        return "\n".join(lines)[:12000]  # truncate
