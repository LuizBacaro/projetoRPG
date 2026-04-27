"""
Service para gerenciamento de arquivos
Princípio SOLID: SRP - Responsável apenas por upload/delete de arquivos

Em produção (CLOUDINARY_* configurado): usa Cloudinary CDN — URLs absolutas e permanentes.
Em desenvolvimento: salva no filesystem local (UPLOADS_DIR).
"""
import uuid
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional
from fastapi import UploadFile
from ..core.config import settings
from ..shared.exceptions.custom_exceptions import InvalidFileError
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

# Regex para detectar componente de versão em URL Cloudinary (ex: v1234567890)
_CLOUDINARY_VERSION_RE = re.compile(r'^v\d+$')


class FileService:
    """
    Service para upload e gerenciamento de arquivos.

    Roteamento automático:
    - CLOUDINARY_* configurado → upload para Cloudinary, retorna URL HTTPS permanente.
    - Sem configuração → salva em UPLOADS_DIR (apenas desenvolvimento).
    """

    def __init__(self):
        self.uploads_dir = settings.UPLOADS_DIR
        self.uploads_base_url = settings.UPLOADS_BASE_URL
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self._cloudinary_ok = bool(
            settings.CLOUDINARY_CLOUD_NAME
            and settings.CLOUDINARY_API_KEY
            and settings.CLOUDINARY_API_SECRET
        )
        if self._cloudinary_ok:
            self._init_cloudinary()

    def _init_cloudinary(self) -> None:
        """Configura o SDK do Cloudinary com as credenciais de settings."""
        import cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        logger.info("✅ Cloudinary configurado para armazenamento de imagens")

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

    @staticmethod
    def _extract_cloudinary_public_id(foto_url: str) -> Optional[str]:
        """
        Extrai o public_id de uma URL Cloudinary para uso na deleção.
        Suporta URLs com e sem componente de versão (v1234567890).
        """
        try:
            parsed = urlparse(foto_url)
            # path: /<cloud>/image/upload[/v<version>]/<public_id>.<ext>
            parts = parsed.path.lstrip('/').split('/')
            upload_idx = parts.index('upload')
            after = parts[upload_idx + 1:]
            # Pula componente de versão opcional
            if after and _CLOUDINARY_VERSION_RE.match(after[0]):
                after = after[1:]
            if not after:
                return None
            # Remove extensão do último segmento
            after[-1] = Path(after[-1]).stem
            return '/'.join(after)
        except (ValueError, IndexError):
            return None

    def validar_arquivo(self, file: UploadFile) -> None:
        """
        Valida extensão, MIME type por magic bytes e tamanho do arquivo.
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

        # Verificar tamanho
        file.file.seek(0, 2)  # ir ao final
        tamanho = file.file.tell()
        file.file.seek(0)  # rebobinar

        if tamanho > self.max_file_size:
            mb = self.max_file_size // (1024 * 1024)
            raise InvalidFileError(f"Arquivo excede o limite de {mb}MB")

    def salvar_arquivo(self, file: UploadFile) -> str:
        """
        Salva um arquivo e retorna a URL pública.
        Usa Cloudinary em produção; filesystem local em desenvolvimento.
        """
        self.validar_arquivo(file)
        if self._cloudinary_ok:
            return self._salvar_cloudinary(file)
        return self._salvar_local(file)

    def _salvar_local(self, file: UploadFile) -> str:
        """Salva no filesystem local (apenas desenvolvimento)."""
        extensao = Path(file.filename).suffix.lower()
        nome_arquivo = f"{uuid.uuid4()}{extensao}"
        caminho_arquivo = self.uploads_dir / nome_arquivo
        with caminho_arquivo.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return self._build_public_url(nome_arquivo)

    def _salvar_cloudinary(self, file: UploadFile) -> str:
        """Faz upload para Cloudinary e retorna URL HTTPS permanente."""
        import cloudinary.uploader
        public_id = f"combatentes/{uuid.uuid4()}"
        result = cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            resource_type="image",
            overwrite=False,
        )
        return result['secure_url']

    def deletar_arquivo(self, foto_url: str) -> bool:
        """
        Deleta um arquivo — Cloudinary (quando configurado e URL absoluta) ou filesystem local.
        """
        if not foto_url:
            return False

        # Cloudinary configurado + URL absoluta → deletar do Cloudinary
        if self._cloudinary_ok and (
            foto_url.startswith("http://") or foto_url.startswith("https://")
        ):
            return self._deletar_cloudinary(foto_url)

        # Demais casos (URL relativa, ou Cloudinary não configurado) → filesystem local
        return self._deletar_local(foto_url)

    def _deletar_local(self, foto_url: str) -> bool:
        """Deleta arquivo do filesystem local com proteção contra path traversal."""
        try:
            nome_arquivo = self._extract_filename(foto_url)
            if not nome_arquivo:
                return False
            caminho_arquivo = self.uploads_dir / nome_arquivo

            caminho_real = caminho_arquivo.resolve()
            dir_real = self.uploads_dir.resolve()
            if not str(caminho_real).startswith(str(dir_real)):
                logger.warning("⚠️ Tentativa de path traversal bloqueada: %s", foto_url)
                return False

            if caminho_real.exists():
                caminho_real.unlink()
                return True
        except Exception as e:
            logger.error("Erro ao deletar arquivo local: %s", e)
        return False

    def _deletar_cloudinary(self, foto_url: str) -> bool:
        """Deleta imagem do Cloudinary via public_id extraído da URL."""
        import cloudinary.uploader
        public_id = self._extract_cloudinary_public_id(foto_url)
        if not public_id:
            logger.warning("⚠️ Não foi possível extrair public_id de: %s", foto_url)
            return False
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            logger.error("Erro ao deletar do Cloudinary: %s", e)
            return False