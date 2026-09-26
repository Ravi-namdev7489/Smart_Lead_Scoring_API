from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from scorer import analyze_lead

app = FastAPI(title="Lead AI Scoring Service")


class LeadRequest(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    message: str
    source: str
    budget: Optional[float] = None
    company: Optional[str] = None
    repeat_lead: bool = False


@app.post("/score")
def score_lead(lead: LeadRequest):
    return analyze_lead(lead.model_dump())