from pydantic import BaseModel


class EvidenceItem(BaseModel):
    extracted_claim: str
    snippet: str
    relevance_score: float        # 0.0 to 1.0
    stance: str                    # "support", "oppose", "neutral"
    evidence_type: str  # "fact", "statistic", "expert_opinion", "policy", "background"
    notes: str


class ExtractorOutput(BaseModel):
    source_summary: str
    source_strengths: list[str]
    source_weaknesses: list[str]
    evidence_items: list[EvidenceItem]
