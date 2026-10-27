"""Estruturas de dados compartilhadas entre as etapas da pipeline."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "ERROR"      # bloqueia a aprovação da observação
    REVIEW = "REVIEW"    # exige decisão humana antes da aprovação
    WARNING = "WARNING"  # observação aprovável, mas com ressalva explícita
    INFO = "INFO"        # registro informativo / rastreabilidade


class IssueClass(str, Enum):
    CONFIRMED_ERROR = "ERRO_CONFIRMADO"
    POSSIBLE_ANOMALY = "POSSIVEL_ANOMALIA"
    LEGIT_EXTREME = "POSSIVEL_VALOR_EXTREMO_LEGITIMO"
    NOT_VALIDATED = "NAO_VALIDADO"
    INFORMATIONAL = "INFORMATIVO"


class ValidationStatus(str, Enum):
    VALID = "VALID"
    VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    ERROR = "ERROR"
    NOT_AVAILABLE = "NOT_AVAILABLE"  # célula com símbolo ou vazia: nada a validar


APPROVABLE = {ValidationStatus.VALID.value, ValidationStatus.VALID_WITH_WARNINGS.value}


class Comparability(str, Enum):
    COMPARABLE = "COMPARABLE"
    COMPARABLE_WITH_CAVEATS = "COMPARABLE_WITH_CAVEATS"
    NOT_COMPARABLE = "NOT_COMPARABLE"
    PENDING_REVIEW = "PENDING_REVIEW"


@dataclass(frozen=True)
class SourceFile:
    """Arquivo físico lido (ou membro de um ZIP)."""

    source_id: str        # caminho lógico: "pasta/arquivo.zip!membro.xlsx"
    file_name: str
    container: str        # ZIP de origem ("" se arquivo solto)
    sha256: str
    size_bytes: int
    fmt: str              # xlsx | xlsm | xls | ods | csv
    duplicate_of: str = ""  # source_id do primeiro arquivo com o mesmo hash


@dataclass
class Issue:
    """Alerta de qualidade com contexto suficiente para revisão humana."""

    rule_id: str
    severity: str
    issue_class: str
    message: str
    recommended_action: str
    source_file: str = ""
    source_sheet: str = ""
    source_cell: str = ""
    observation_id: str = ""
    table_id: str = ""
    observed_value: str = ""
    context: str = ""
    stage: str = ""
    review_status: str = "PENDENTE"
    issue_id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.issue_id:
            key = "|".join([self.rule_id, self.source_file, self.source_sheet, self.source_cell,
                            self.observation_id, self.context, self.message])
            self.issue_id = "ISS-" + hashlib.sha1(key.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def stable_id(*parts: Any, prefix: str = "", length: int = 16) -> str:
    """Identificador determinístico (mesma entrada -> mesmo id em toda execução)."""
    digest = hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:length]
    return f"{prefix}{digest}"
