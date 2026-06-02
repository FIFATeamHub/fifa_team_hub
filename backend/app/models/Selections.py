from sqlalchemy.orm import registry, Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime
import uuid

registro_tabela = registry()

@registro_tabela.mapped_as_dataclass #Mapeia a tabela/planilha como uma dataclass(classe sem métodos)
class Selections:
    __tablename__ = "Selections" 

    id: Mapped[uuid.UUID] = mapped_column(primary_key = True)

    name: Mapped[str]

    code: Mapped[str] = mapped_column(String(3), unique = True)
    
    created_at: Mapped[datetime]