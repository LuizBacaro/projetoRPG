"""
Service para gerenciamento de arquivos
Princípio SOLID: SRP - Responsável apenas por upload/delete de arquivos
"""
import uuid
import shutil
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional
from fastapi import UploadFile
from ..core.config import settings
from ..exceptions.custom_exceptions import InvalidFileError
import logging

logger = logging.getLogger(__name__)

# Assinaturas mágicas (magic bytes) para tipos de imagem permitidos
_MAGIC_BYTES = {
    b'\xff\xd8\xff': '.jpg',      # JPEG
    b'\x89PNG\r\n\x1a\n': '.png', # PNG
    b'GIF87a': '.gif',             # GIF87
    b'GIF89a': '.gif',             # GIF89
    b'RIFF': '.webp',              # WebP (RIFF container)
}


class FileService:
    """
    Service para upload e gerenciamento de arquivos
    """
    
    def __init__(self):
        self.uploads_dir = settings.UPLOADS_DIR
        self.uploads_base_url = settings.UPLOADS_BASE_URL
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS

    def _build_public_url(self, nome_arquivo: str) -> str:
        base_url = (self.uploads_base_url or "/uploads").strip()
        if not base_url:
            base_url = "/uploads"
        return f"{base_url.rstrip('/')}/{nome_arquivo}"

    @staticmethod
    def _extract_filename(foto_url: str) -> str:
        parsed = urlparse(foto_url or "")
        path = parsed.path or foto_url
        return Path(path).name
    
    def validar_arquivo(self, file: UploadFile) -> None:
        """
        Valida extensão, MIME type por magic bytes e tamanho do arquivo
        """
        # Verificar extensão
        extensao = Path(file.filename).suffix.lower()
        if extensao not in self.allowed_extensions:
            raise InvalidFileError(
                f"Extensão '{extensao}' não permitida. "
                f"Permitidas: {', '.join(self.allowed_extensions)}"
            )

        # Ler cabeçalho para verificar magic bytes
        header = file.file.read(16)
        file.file.seek(0)  # rebobinar

        tipo_real = None
        for magic, ext in _MAGIC_BYTES.items():
            if header.startswith(magic):
                tipo_real = ext
                break
        # WebP: RIFF + tamanho + WEBP
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            tipo_real = '.webp'

        if tipo_real is None:
            raise InvalidFileError(
                "Conteúdo do arquivo não corresponde a um formato de imagem válido"
            )

        # Verificar tamanho lendo até o limite
        file.file.seek(0, 2)  # ir ao final
        tamanho = file.file.tell()
        file.file.seek(0)  # rebobinar

        if tamanho > self.max_file_size:
            mb = self.max_file_size // (1024 * 1024)
            raise InvalidFileError(f"Arquivo excede o limite de {mb}MB")
    
    def salvar_arquivo(self, file: UploadFile) -> str:
        """
        Salva um arquivo e retorna a URL relativa
        """
        self.validar_arquivo(file)
        
        # Gerar nome único
        extensao = Path(file.filename).suffix.lower()
        nome_arquivo = f"{uuid.uuid4()}{extensao}"
        caminho_arquivo = self.uploads_dir / nome_arquivo
        
        # Salvar arquivo
        with caminho_arquivo.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return self._build_public_url(nome_arquivo)
    
    def deletar_arquivo(self, foto_url: str) -> bool:
        """
        Deleta um arquivo do sistema — valida que o path é dentro de uploads_dir
        """
        if not foto_url:
            return False
        
        try:
            # Extrair apenas o nome do arquivo (previne path traversal)
            nome_arquivo = self._extract_filename(foto_url)
            if not nome_arquivo:
                return False
            caminho_arquivo = self.uploads_dir / nome_arquivo

            # Garantir que o caminho resolvido está DENTRO de uploads_dir
            caminho_real = caminho_arquivo.resolve()
            dir_real = self.uploads_dir.resolve()
            if not str(caminho_real).startswith(str(dir_real)):
                logger.warning(f"⚠️ Tentativa de path traversal bloqueada: {foto_url}")
                return False

            if caminho_real.exists():
                caminho_real.unlink()
                return True
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
        
        return False