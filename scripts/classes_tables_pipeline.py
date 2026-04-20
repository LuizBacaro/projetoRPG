"""
Pipeline de tabelas de classes (D&D 3.5).

Objetivo:
- Ler os arquivos Excel de `tabelas_classes_excel/`.
- Normalizar o conteúdo em um formato consistente.
- Exportar para JSON sem alterar nenhum fluxo existente de seed/API.

Este módulo foi criado para suportar uma evolução incremental com baixo risco,
seguindo separação de responsabilidades (SOLID/Clean Code) e mantendo
retrocompatibilidade com o projeto atual.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass(frozen=True)
class ClassTableDocument:
    table_number: int
    title: str
    source_file: str
    metadata: dict[str, str]
    raw_lines: list[str]
    segmented_rows: list[list[str]]


@dataclass(frozen=True)
class NormalizedClassTable:
    table_number: int
    title: str
    source_file: str
    metadata: dict[str, str]
    header: list[str]
    rows: list[dict[str, str]]


class ClassTableWorkbookReader:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def list_workbooks(self) -> list[Path]:
        if not self.base_dir.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {self.base_dir}")
        files = sorted(self.base_dir.glob("Tabela_3-*.xlsx"))
        if not files:
            raise FileNotFoundError(f"Nenhuma planilha encontrada em: {self.base_dir}")
        return files

    def read_all(self) -> list[ClassTableDocument]:
        documents: list[ClassTableDocument] = []
        for workbook_path in self.list_workbooks():
            documents.append(self._read_single(workbook_path))
        return documents

    def _read_single(self, workbook_path: Path) -> ClassTableDocument:
        wb = load_workbook(workbook_path, data_only=True)
        if "Metadados" not in wb.sheetnames or "ExtracaoBruta" not in wb.sheetnames:
            raise ValueError(
                f"Planilha sem abas esperadas (Metadados/ExtracaoBruta): {workbook_path.name}"
            )

        metadata = self._read_metadata(wb["Metadados"])
        table_number = self._extract_table_number(metadata)
        title = metadata.get("Título", workbook_path.stem)
        raw_lines = self._read_single_column_rows(wb["ExtracaoBruta"], skip_header=True)
        segmented_rows = (
            self._read_segmented_rows(wb["Segmentado"]) if "Segmentado" in wb.sheetnames else []
        )

        return ClassTableDocument(
            table_number=table_number,
            title=title,
            source_file=workbook_path.name,
            metadata=metadata,
            raw_lines=raw_lines,
            segmented_rows=segmented_rows,
        )

    @staticmethod
    def _read_metadata(sheet) -> dict[str, str]:
        metadata: dict[str, str] = {}
        for row in sheet.iter_rows(min_row=2, values_only=True):
            key = str(row[0]).strip() if row and row[0] is not None else ""
            value = str(row[1]).strip() if row and len(row) > 1 and row[1] is not None else ""
            if key:
                metadata[key] = value
        return metadata

    @staticmethod
    def _extract_table_number(metadata: dict[str, str]) -> int:
        raw = metadata.get("Tabela", "").strip()
        # Ex.: "3-18" -> 18
        if "-" in raw:
            suffix = raw.split("-", maxsplit=1)[1]
        else:
            suffix = raw
        try:
            return int(suffix)
        except ValueError as exc:
            raise ValueError(f"Número de tabela inválido em metadata: {raw!r}") from exc

    @staticmethod
    def _read_single_column_rows(sheet, skip_header: bool) -> list[str]:
        rows: list[str] = []
        min_row = 2 if skip_header else 1
        for row in sheet.iter_rows(min_row=min_row, values_only=True):
            value = row[0] if row else None
            if value is None:
                continue
            text = str(value).strip()
            if text:
                rows.append(text)
        return rows

    @staticmethod
    def _read_segmented_rows(sheet) -> list[list[str]]:
        rows: list[list[str]] = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            values = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if values:
                rows.append(values)
        return rows


class ClassTableNormalizer:
    """
    Normaliza o conteúdo segmentado em um formato tabular previsível.

    Estratégia:
    - Usa a primeira linha segmentada como cabeçalho.
    - Linhas seguintes são mapeadas por posição.
    - Células faltantes são preenchidas com string vazia para manter shape estável.
    """

    def normalize(self, document: ClassTableDocument) -> NormalizedClassTable:
        segmented = document.segmented_rows
        if not segmented:
            return NormalizedClassTable(
                table_number=document.table_number,
                title=document.title,
                source_file=document.source_file,
                metadata=document.metadata,
                header=[],
                rows=[],
            )

        cleaned_segmented = [
            row
            for row in segmented
            if not (row and row[0].lower().startswith("tabela 3-"))
        ]
        if not cleaned_segmented:
            cleaned_segmented = segmented

        header_index = self._detect_header_index(cleaned_segmented)
        explicit_header = cleaned_segmented[header_index]
        has_semantic_header = self._looks_like_header(explicit_header)
        max_cols = max(len(r) for r in cleaned_segmented) if cleaned_segmented else 0
        header = (
            explicit_header
            if has_semantic_header
            else [f"col_{i}" for i in range(1, max_cols + 1)]
        )
        rows: list[dict[str, str]] = []
        data_rows = (
            cleaned_segmented[header_index + 1 :]
            if has_semantic_header
            else cleaned_segmented
        )
        for row in data_rows:
            if self._is_noise_row(row):
                continue
            row_dict = self._row_to_dict(header, row)
            if any(v for v in row_dict.values()):
                rows.append(row_dict)

        return NormalizedClassTable(
            table_number=document.table_number,
            title=document.title,
            source_file=document.source_file,
            metadata=document.metadata,
            header=header,
            rows=rows,
        )

    @staticmethod
    def _row_to_dict(header: list[str], row: list[str]) -> dict[str, str]:
        result: dict[str, str] = {}
        for idx, col_name in enumerate(header):
            result[col_name] = row[idx] if idx < len(row) else ""
        return result

    @staticmethod
    def _detect_header_index(rows: list[list[str]]) -> int:
        """
        Seleciona o cabeçalho com base na maior quantidade de colunas
        entre as primeiras linhas (heurística robusta para tabelas variadas).
        """
        scan_limit = min(15, len(rows))
        best_index = 0
        best_width = len(rows[0]) if rows else 0
        for idx in range(scan_limit):
            width = len(rows[idx])
            if width > best_width:
                best_width = width
                best_index = idx
        return best_index

    @staticmethod
    def _is_noise_row(row: list[str]) -> bool:
        if not row:
            return True
        first = row[0].strip().lower()
        if not first:
            return True
        if first.startswith("capítulo"):
            return True
        if first.startswith("características da classe"):
            return True
        return False

    @staticmethod
    def _looks_like_header(row: list[str]) -> bool:
        if not row:
            return False
        joined = " ".join(row).strip().lower()
        header_hints = [
            "nível",
            "nivel",
            "bônus",
            "bonus",
            "fortitude",
            "reflexos",
            "vontade",
            "especial",
            "tipo",
            "exemplos",
            "magias",
            "deus",
            "tendência",
            "tendencia",
        ]
        return any(h in joined for h in header_hints)


class ClassTableCatalogExporter:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def export(self, tables: list[NormalizedClassTable]) -> Path:
        payload: dict[str, Any] = {
            "schema_version": 1,
            "generated_from": "tabelas_classes_excel",
            "tables": [asdict(table) for table in tables],
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.output_path


class ClassTablePipeline:
    def __init__(
        self,
        reader: ClassTableWorkbookReader,
        normalizer: ClassTableNormalizer,
        exporter: ClassTableCatalogExporter,
    ) -> None:
        self.reader = reader
        self.normalizer = normalizer
        self.exporter = exporter

    def run(self) -> Path:
        docs = self.reader.read_all()
        normalized = [self.normalizer.normalize(doc) for doc in docs]
        normalized.sort(key=lambda t: t.table_number)
        return self.exporter.export(normalized)
