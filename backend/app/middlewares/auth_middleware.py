from functools import wraps
from flask import request, g, jsonify
from jose import JWTError, ExpiredSignatureError

from app.services.auth import decodificar_token


#autenticação
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        #verifica se o header existe e tem formato bearer <token>
        if not auth_header.startswith("Bearer "):
            return jsonify({"error" : "Token não fornecido"}), 401

        token = auth_header.split(" ")[1]

        #decodifica o token e popula o flask.g
        try:
            payload = decodificar_token(token)
            g.current_user_id = payload["sub"]
            g.current_user_role = payload["role"]
            g.current_selection_id = payload["selection_id"]
        
        except ExpiredSignatureError:
            return jsonify({"error" : "Token expirado"}), 401

        except JWTError:
            return jsonify({"error" : "Token inválido"}), 401
        
        return f(*args, **kwargs)
    
    return decorated


#autorização, quem está autorizado a acessar a rota
def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            #lê a role do g (preenchido pelo require_auth)
            if g.current_user_role not in roles:
                return jsonify({"error" : "Acesso negado: permissão insuficiente"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator