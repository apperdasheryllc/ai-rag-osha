"""Pydantic request/response models for API endpoints."""
from pydantic import BaseModel, Field

class OshaStandardQuery(BaseModel):
    query: str = Field(..., min_length=1, description="OSHA PPE question")
    results: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "When are safety nets required in construction?",
                "results": 5,
            }
        }
    }


class OshaSource(BaseModel):
    citation: str = Field(description="Regulatory citation extracted from the source chunk")
    label: str = Field(description="Human-readable OSHA section label")
    source_url: str = Field(description="Original OSHA source URL")
    text: str = Field(description="Retrieved source chunk text")


class OshaStandardResponse(BaseModel):
    answer: str = Field(description="Model-generated answer grounded in retrieved OSHA chunks")
    sources: list[OshaSource] = Field(description="Chunks used to generate the answer")

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": (
                    "Safety nets are required when workplaces are more than 25 feet above the "
                    "ground and other fall protection is impractical (1926.105(a))."
                ),
                "sources": [
                    {
                        "citation": "1926.105(a)",
                        "label": "1926.105 - Safety nets.",
                        "source_url": "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.105",
                        "text": "Safety nets shall be provided when workplaces are more than 25 feet above...",
                    }
                ],
            }
        }
    }
