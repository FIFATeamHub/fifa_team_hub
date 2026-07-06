from flask import Blueprint

from app.controllers.auth import register, login, me
from app.middlewares.auth import token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.post("/register")
def route_register():
    return register()


@auth_bp.post("/login")
def route_login():
    return login()

@auth_bp.get("/me")
@token_required
def route_me(current_user):
    # current_user injetado pelo decorator token_required
    return me(current_user)
