from pydantic import BaseModel


class ReportClaim(BaseModel):
    text: str
    citation_ids: list[str]


class ReportSection(BaseModel):
    heading: str
    claims: list[ReportClaim]
