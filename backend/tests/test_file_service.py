from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

from app.shared.exceptions.custom_exceptions import InvalidFileError
from app.services.file_service import FileService


def _png_upload(filename: str = "avatar.png", payload_size: int = 16) -> UploadFile:
    content = b"\x89PNG\r\n\x1a\n" + (b"x" * payload_size)
    return UploadFile(filename=filename, file=BytesIO(content))


def test_validar_arquivo_rejeita_extensao_invalida(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    service = FileService()
    arquivo = UploadFile(filename="avatar.exe", file=BytesIO(b"MZ123456"))

    try:
        service.validar_arquivo(arquivo)
        assert False, "Deveria falhar para extensão inválida"
    except InvalidFileError as exc:
        assert "Extensão" in str(exc)


def test_validar_arquivo_rejeita_magic_bytes_invalido(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    service = FileService()
    arquivo = UploadFile(filename="avatar.png", file=BytesIO(b"NAO_E_IMAGEM"))

    try:
        service.validar_arquivo(arquivo)
        assert False, "Deveria falhar para magic bytes inválidos"
    except InvalidFileError as exc:
        assert "formato de imagem" in str(exc)


def test_salvar_arquivo_grava_em_uploads(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    service = FileService()
    foto_url = service.salvar_arquivo(_png_upload())

    nome_arquivo = Path(foto_url).name
    assert foto_url.startswith("/uploads/")
    assert (tmp_path / nome_arquivo).exists()


def test_salvar_arquivo_usa_uploads_base_url_configuravel(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_BASE_URL", "https://cdn.example.com/uploads")
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    service = FileService()
    foto_url = service.salvar_arquivo(_png_upload())

    assert foto_url.startswith("https://cdn.example.com/uploads/")
    assert (tmp_path / Path(foto_url).name).exists()


def test_deletar_arquivo_remove_arquivo_existente(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    service = FileService()
    foto_url = service.salvar_arquivo(_png_upload())

    assert service.deletar_arquivo(foto_url) is True
    assert not (tmp_path / Path(foto_url).name).exists()


def test_deletar_arquivo_path_traversal_nao_remove(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    service = FileService()

    assert service.deletar_arquivo("/uploads/../../etc/passwd") is False


def test_deletar_arquivo_com_url_absoluta(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_BASE_URL", "https://cdn.example.com/uploads")
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    service = FileService()
    foto_url = service.salvar_arquivo(_png_upload())

    assert service.deletar_arquivo(foto_url) is True