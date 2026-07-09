from flask import jsonify
from app.models.selection import Selection

def list_selections():
    selections = Selection.query.order_by(Selection.name).all()

    return jsonify([
        {
            "id": str(s.id),
            "name": s.name,
            "code": s.code
        }
        for s in selections
    ])