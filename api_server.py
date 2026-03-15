"""
FastAPI server exposing clinical_decision_support() as a REST endpoint.
Run with:  uvicorn api_server:app --host 0.0.0.0 --port 8100 --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_search import clinical_decision_support

app = FastAPI(title="ChronoChart Guidelines API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GuidelineRequest(BaseModel):
    patient_summary: str


class GuidelineResponse(BaseModel):
    status: str          # "NO_CHANGE" | "CHANGE_RECOMMENDED"
    rationale: str
    action: str
    citations: list[str]


@app.post("/api/guidelines", response_model=GuidelineResponse)
def get_guidelines(req: GuidelineRequest):
    try:
        result = clinical_decision_support(req.patient_summary)
        return GuidelineResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
