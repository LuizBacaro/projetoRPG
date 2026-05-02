"""Armazenamento de ficheiros (uploads / CDN) — agnóstico de jogo."""

from app.services.file_service import FileService


def get_file_service() -> FileService:
    return FileService()
