"""Logging estruturado: JSON Lines em arquivo + mensagens legíveis no console."""
from __future__ import annotations

import json
import logging
from pathlib import Path

_RESERVED = set(vars(logging.makeLogRecord({})).keys()) | {"message", "asctime"}


class JsonLinesFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        payload.update({k: v for k, v in vars(record).items() if k not in _RESERVED})
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging(log_dir: Path, verbose: bool = False) -> logging.Logger:
    """Configura o logger raiz ``pense``. Idempotente (não duplica handlers)."""
    logger = logging.getLogger("pense")
    logger.setLevel(logging.DEBUG)
    for h in list(logger.handlers):
        logger.removeHandler(h)
        h.close()
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / "pipeline.jsonl", mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(JsonLinesFormatter())
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"pense.{name}")
