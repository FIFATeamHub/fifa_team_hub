from flask import Blueprint

from app.controllers.auth import (
    list_pending_registrations,
    approve_registration,
    reject_registration,
)
from app.middlewares.auth import token_required

registration_bp = Blueprint("registration", __name__, url_prefix="/api/auth")


@registration_bp.get("/registrations/pending")
@token_required
def route_list_pending_registrations(current_user):
    return list_pending_registrations(current_user)


@registration_bp.post("/registrations/<uuid:user_id>/approve")
@token_required
def route_approve_registration(current_user, user_id):
    return approve_registration(current_user, user_id)


@registration_bp.post("/registrations/<uuid:user_id>/reject")
@token_required
def route_reject_registration(current_user, user_id):
    return reject_registration(current_user, user_id)
