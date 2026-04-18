from pydantic import BaseModel


class ReportSection(BaseModel):
    heading: str
    content: str


class WriterOutput(BaseModel):
    answer_summary: str
    sections: list[ReportSection]
    limitations: list[str]
    confidence: str   # "high", "medium", "low"
