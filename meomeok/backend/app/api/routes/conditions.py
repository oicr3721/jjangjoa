from fastapi import APIRouter
from app.data.condition_groups import CONDITION_GROUPS

router = APIRouter()

@router.get("/conditions")
def get_conditions():

    return [
        {
            "key": key,
            "label": value["label"],
            "emoji": value["emoji"]
        }
        for key, value in CONDITION_GROUPS.items()
    ]