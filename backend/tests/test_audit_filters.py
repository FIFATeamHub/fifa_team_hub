import uuid
from datetime import datetime

from app.models.audit_log import AuditLog
from app.models.enums.user_role import LogAction


def test_filtro_por_periodo(app, client, db, selection_bra, token_bra_auditor):
    with app.app_context():
        db.add(AuditLog(
            user_id=None,
            action=LogAction.LOGIN,
            resource_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            status="SUCCESS",
            details="log dentro do periodo",
            selection_id=selection_bra,
            created_at=datetime(2026, 7, 15, 15, 0, 0),
        ))
        db.add(AuditLog(
            user_id=None,
            action=LogAction.LOGIN,
            resource_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            status="SUCCESS",
            details="log antes do periodo",
            selection_id=selection_bra,
            created_at=datetime(2026, 7, 10, 15, 0, 0),
        ))
        db.add(AuditLog(
            user_id=None,
            action=LogAction.LOGIN,
            resource_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            status="SUCCESS",
            details="log depois do periodo",
            selection_id=selection_bra,
            created_at=datetime(2026, 7, 20, 15, 0, 0),
        ))
        db.commit()

    response = client.get(
        "/api/audit/?start_date=2026-07-14&end_date=2026-07-16",
        headers={"Authorization": f"Bearer {token_bra_auditor}"}
    )

    assert response.status_code == 200
    details = [row["details"] for row in response.json["data"]]
    assert "log dentro do periodo" in details
    assert "log antes do periodo" not in details
    assert "log depois do periodo" not in details


def test_filtro_por_user_id(app, client, db, selection_bra, token_bra_auditor):
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()

    with app.app_context():
        db.add(AuditLog(
            user_id=user_a,
            action=LogAction.LOGIN,
            resource_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            status="SUCCESS",
            details="log do usuario A",
            selection_id=selection_bra,
        ))
        db.add(AuditLog(
            user_id=user_b,
            action=LogAction.LOGIN,
            resource_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            status="SUCCESS",
            details="log do usuario B",
            selection_id=selection_bra,
        ))
        db.commit()

    response = client.get(
        f"/api/audit/?user_id={user_a}",
        headers={"Authorization": f"Bearer {token_bra_auditor}"}
    )

    assert response.status_code == 200
    details = [row["details"] for row in response.json["data"]]
    assert "log do usuario A" in details
    assert "log do usuario B" not in details
