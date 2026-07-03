from flask import Blueprint
from app.controllers.selection import list_selections

selection_bp = Blueprint(
    "selection",
    __name__,
    url_prefix="/api/selection"
)

@selection_bp.get("/")
def route_list():
    return list_selections()