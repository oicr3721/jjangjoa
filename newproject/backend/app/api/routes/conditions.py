# app/api/routes/conditions.py
from fastapi import APIRouter
from app.data.condition_rules import CONDITION_RULES

router = APIRouter()

@router.get("/conditions")
def get_conditions():
    return {"conditions": list(CONDITION_RULES.keys())}
