"""
Service para gerenciamento de arquivos
Princípio SOLID: SRP - Responsável apenas por upload/delete de arquivos
"""
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from ..core.config import settings
from ..exceptions.custom_exceptions import InvalidFileError


class FileService:
    """
    Service para upload e gerenciamento de arquivos
    """
    
    def __init__(self):
        self.uploads_dir = settings.UPLOADS_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
    
    def validar_arquivo(self, file: UploadFile) -> None:
        """
        Valida se o arquivo é permitido
        """
        # Verificar extensão
        extensao = Path(file.filename).suffix.lower()
        if extensao not in self.allowed_extensions:
            raise InvalidFileError(
                f"Extensão '{extensao}' não permitida. "
                f"Permitidas: {', '.join(self.allowed_extensions)}"
            )
    
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
        
        return f"/uploads/{nome_arquivo}"
    
    def deletar_arquivo(self, foto_url: str) -> bool:
        """
        Deleta um arquivo do sistema
        """
        if not foto_url:
            return False
        
        try:
            caminho_arquivo = settings.BASE_DIR / foto_url.lstrip('/')
            if caminho_arquivo.exists():
                caminho_arquivo.unlink()
                return True
        except Exception as e:
            print(f"Erro ao deletar arquivo: {e}")
        
        return False