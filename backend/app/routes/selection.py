from flask import Blueprint
from app.controllers.selection import create_selection, list_selections
from app.middlewares.auth import token_required

selection_bp = Blueprint(
    "selection",
    __name__,
    url_prefix="/api/selection"
)

@selection_bp.get("/")
def route_list():
    return list_selections()

@selection_bp.post("/")
@token_required
def route_create(current_user):
    return create_selection(current_user)