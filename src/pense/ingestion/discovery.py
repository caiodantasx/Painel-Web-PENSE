"""Descoberta de arquivos de entrada, inclusive dentro de ZIPs.

ZIPs são lidos em memória (sem extração para disco), o que elimina o risco de
*zip slip*. Há limites de tamanho e de quantidade de membros contra *zip bombs*.
Arquivos idênticos (mesmo SHA-256) são registrados como duplicados e
processados uma única vez.
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ..config import Config
from ..logging_utils import get_logger
from ..models import Issue, IssueClass, Severity, SourceFile

log = get_logger("ingestion")


@dataclass
class RawItem:
    source: SourceFile
    data: bytes


@dataclass
class DiscoveryResult:
    items: list[RawItem]            # arquivos únicos a processar
    all_sources: list[SourceFile]   # inventário completo (inclui duplicados e ZIPs)
    issues: list[Issue]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_hidden(name: str) -> bool:
    parts = PurePosixPath(name).parts
    return any((p.startswith(".") and p not in (".", "..")) or p.startswith("__MACOSX") or p.startswith("~$")
               for p in parts)


def _has_traversal(name: str) -> bool:
    p = PurePosixPath(name.replace("\\", "/"))
    return p.is_absolute() or ".." in p.parts


class Discoverer:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        ing = cfg.settings["ingestion"]
        self.supported = {e.lower() for e in ing["supported_extensions"]}
        self.archives = {e.lower() for e in ing["archive_extensions"]}
        self.max_depth = int(ing["max_archive_depth"])
        self.max_member = int(ing["max_member_bytes"])
        self.max_members = int(ing["max_members_per_archive"])
        self.skip_hidden = bool(ing["skip_hidden"])
        self.issues: list[Issue] = []
        self.sources: list[SourceFile] = []
        self.items: list[RawItem] = []
        self._seen: dict[str, str] = {}

    # ------------------------------------------------------------------ API
    def run(self, raw_dir: Path) -> DiscoveryResult:
        for path in sorted(p for p in raw_dir.rglob("*") if p.is_file()):
            rel = path.relative_to(raw_dir).as_posix()
            if self.skip_hidden and _is_hidden(rel):
                continue
            ext = path.suffix.lower()
            if ext not in self.supported and ext not in self.archives:
                self._issue("ING001", Severity.INFO, f"Extensão não suportada ignorada: {ext}", rel,
                            "Converter para um formato suportado se o arquivo contiver tabelas.")
                continue
            try:
                data = path.read_bytes()
            except OSError as exc:  # arquivo ilegível não interrompe a execução
                self._issue("ING002", Severity.ERROR, f"Falha de leitura do arquivo: {exc}", rel,
                            "Verificar permissões/integridade do arquivo.")
                continue
            self._register(rel, path.name, "", data, depth=0)
        log.info("Descoberta concluída", extra={"unique_files": len(self.items),
                                                "inventoried": len(self.sources)})
        return DiscoveryResult(self.items, self.sources, self.issues)

    # ------------------------------------------------------------ internals
    def _register(self, source_id: str, name: str, container: str, data: bytes, depth: int) -> None:
        ext = PurePosixPath(name).suffix.lower()
        digest = sha256_bytes(data)
        dup = self._seen.get(digest, "")
        src = SourceFile(source_id=source_id, file_name=name, container=container, sha256=digest,
                         size_bytes=len(data), fmt=ext.lstrip("."), duplicate_of=dup)
        self.sources.append(src)
        if dup:
            log.info("Arquivo duplicado (mesmo SHA-256) — não reprocessado",
                     extra={"source": source_id, "duplicate_of": dup})
            return
        self._seen[digest] = source_id
        if ext in self.archives:
            self._expand_zip(source_id, data, depth)
        elif ext in self.supported:
            self.items.append(RawItem(src, data))

    def _expand_zip(self, source_id: str, data: bytes, depth: int) -> None:
        if depth >= self.max_depth:
            self._issue("ING003", Severity.WARNING, "ZIP aninhado além da profundidade máxima", source_id,
                        "Extrair manualmente ou aumentar max_archive_depth.")
            return
        try:
            zf = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile as exc:
            self._issue("ING004", Severity.ERROR, f"ZIP corrompido: {exc}", source_id,
                        "Baixar novamente o arquivo da fonte oficial.")
            return
        members = [m for m in zf.infolist() if not m.is_dir()]
        if len(members) > self.max_members:
            self._issue("ING005", Severity.ERROR, f"ZIP com {len(members)} membros excede o limite", source_id,
                        "Verificar o conteúdo do ZIP.")
            return
        for info in sorted(members, key=lambda m: m.filename):
            name = info.filename
            if self.skip_hidden and _is_hidden(name):
                continue
            ext = PurePosixPath(name).suffix.lower()
            if ext not in self.supported and ext not in self.archives:
                continue
            if _has_traversal(name):
                # Nada é extraído para disco, então não há risco de escrita fora da pasta;
                # o membro é lido em memória e o caminho suspeito fica registrado.
                self._issue("ING008", Severity.WARNING, "Membro de ZIP com caminho absoluto ou '..' "
                            "(lido apenas em memória)", f"{source_id}!{name}",
                            "Verificar a origem do ZIP; obter o arquivo da fonte oficial.")
            if info.file_size > self.max_member:
                self._issue("ING006", Severity.ERROR, f"Membro excede {self.max_member} bytes", f"{source_id}!{name}",
                            "Verificar se o arquivo é legítimo.")
                continue
            try:
                member_data = zf.read(info)
            except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
                self._issue("ING007", Severity.ERROR, f"Falha ao ler membro do ZIP: {exc}", f"{source_id}!{name}",
                            "Verificar integridade do ZIP.")
                continue
            self._register(f"{source_id}!{name}", PurePosixPath(name).name, source_id, member_data, depth + 1)

    def _issue(self, rule: str, sev: Severity, msg: str, source: str, action: str) -> None:
        cls = IssueClass.CONFIRMED_ERROR if sev == Severity.ERROR else IssueClass.INFORMATIONAL
        self.issues.append(Issue(rule_id=rule, severity=sev.value, issue_class=cls.value, message=msg,
                                 recommended_action=action, source_file=source, stage="ingestion"))
        log.log(40 if sev == Severity.ERROR else 20, msg, extra={"source": source, "rule": rule})


def discover(cfg: Config, raw_dir: Path | None = None) -> DiscoveryResult:
    return Discoverer(cfg).run(raw_dir or cfg.path("raw"))
