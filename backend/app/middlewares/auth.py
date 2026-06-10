from functools import wraps
from flask import request, jsonify

from app.models.user import User
from app.services.auth import decodificar_token

from jose import JWTError


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Pega o header Authorization
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token ausente"}), 401

        # Verifica formato "Bearer <token>"
        partes = auth_header.split(" ")
        if len(partes) != 2 or partes[0] != "Bearer":
            return jsonify({"error": "Formato de token inválido. Use: Bearer <token>"}), 401

        token = partes[1]

        # Decodifica e valida o token - agora com exceção se inválido
        try:
            payload = decodificar_token(token)
        except JWTError:
            return jsonify({"error": "Token inválido ou expirado"}), 401
        
        # Busca o usuário no banco pelo sub (user_id)
        current_user = User.query.get(payload["sub"])
        if current_user is None:
            return jsonify({"error": "Usuário não encontrado"}), 401

        # Injeta current_user como primeiro argumento da função decorada
        return f(current_user, *args, **kwargs)

    return decorated
