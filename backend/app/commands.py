import click

from app.extensions import db
from app.models.selection import Selection
from app.models.user import User
from app.models.enums.user_role import RegistrationStatus, UserRole
from app.services.auth import hash_password


def register_commands(app):
    @app.cli.command("bootstrap")
    @click.option("--organizer-name", default="Administrador do Sistema", show_default=True)
    @click.option("--organizer-email", envvar="BOOTSTRAP_ORGANIZER_EMAIL", required=True)
    @click.option("--organizer-password", envvar="BOOTSTRAP_ORGANIZER_PASSWORD", required=True)
    @click.option("--selection-name", default="Seleção Inicial", show_default=True)
    @click.option("--selection-code", default="FFA", show_default=True)
    @click.option("--auditor-name", default="Auditor Inicial", show_default=True)
    @click.option("--auditor-email", envvar="BOOTSTRAP_AUDITOR_EMAIL", required=True)
    @click.option("--auditor-password", envvar="BOOTSTRAP_AUDITOR_PASSWORD", required=True)
    def bootstrap(
        organizer_name,
        organizer_email,
        organizer_password,
        selection_name,
        selection_code,
        auditor_name,
        auditor_email,
        auditor_password,
    ):
        """Cria o Organizador inicial e a primeira Selection (com seu Auditor), permitindo o primeiro uso do sistema."""
        if Selection.query.count() > 0 or User.query.count() > 0:
            click.echo("Banco já contém dados — bootstrap ignorado.")
            return

        organizer = User(
            full_name=organizer_name,
            email=organizer_email.strip().lower(),
            password_hash=hash_password(organizer_password),
            role=UserRole.ORGANIZER,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=None,
        )
        db.session.add(organizer)

        selection = Selection(name=selection_name, code=selection_code.strip().upper())
        db.session.add(selection)
        db.session.flush()

        auditor = User(
            full_name=auditor_name,
            email=auditor_email.strip().lower(),
            password_hash=hash_password(auditor_password),
            role=UserRole.AUDITOR,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=selection.id,
        )
        db.session.add(auditor)

        db.session.commit()

        click.echo(
            f"Bootstrap concluído: ORGANIZER '{organizer.email}', "
            f"Selection '{selection.code}' e AUDITOR '{auditor.email}' criados."
        )
