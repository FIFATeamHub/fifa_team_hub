from flask import Blueprint

from app.controllers.auth import register, login, me
from app.middlewares.auth_middleware import require_auth

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def route_register():
    return register()


@auth_bp.post("/login")
def route_login():
    return login()


@auth_bp.get("/me")
@require_auth
def route_me():
    #os dados ficam em flask.g a rota lê g.current_user_id quando precisar
    return me()
