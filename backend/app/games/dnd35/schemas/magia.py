"""Schemas Pydantic de Magias (D&D 3.5) — canônico em `app.games.dnd35.schemas.magia`."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class MagiaClasseNivel(BaseModel):
    classe: str = Field(..., min_length=1, max_length=50)
    nivel: int = Field(..., ge=0, le=9)


class MagiaClasseNivelResponse(MagiaClasseNivel):
    id: int

    class Config:
        from_attributes = True


class MagiaBase(BaseModel):
    """Schema base com campos comuns"""

    nome: str = Field(..., min_length=1, max_length=100)
    nome_en: Optional[str] = Field(default=None, max_length=100)
    nivel: int = Field(..., ge=0, le=9)
    classe: str = Field(..., min_length=1, max_length=120)
    escola: Optional[str] = Field(default=None, max_length=50)
    sub_escola: Optional[str] = Field(default=None, max_length=50)
    descritor: Optional[str] = Field(default=None, max_length=200)
    componentes: Optional[str] = Field(default=None, max_length=20)
    componente_extra: Optional[str] = Field(default=None, max_length=300)
    alcance: Optional[str] = Field(default=None, max_length=50)
    area_efeito: Optional[str] = Field(default=None, max_length=100)
    duracao: Optional[str] = Field(default=None, max_length=100)
    tempo_conjuracao: Optional[str] = Field(default=None, max_length=50)
    dano: Optional[str] = Field(default=None, max_length=50)
    teste_resistencia: Optional[str] = Field(default=None, max_length=50)
    resistencia_magica: bool = False
    resistencia_magia_texto: Optional[str] = Field(default=None, max_length=50)
    descricao: Optional[str] = Field(default=None, max_length=1000)
    descricao_en: Optional[str] = Field(default=None, max_length=1000)
    ativo: bool = True
    e_magia_dominio: bool = False
    dominios: Optional[str] = Field(default=None, max_length=250)
    pagina_referencia: Optional[int] = Field(default=None, ge=1)


class MagiaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    nome_en: Optional[str] = Field(default=None, max_length=100)
    escola: str = Field(..., min_length=1, max_length=50)
    sub_escola: Optional[str] = Field(default=None, max_length=50)
    descritor: Optional[str] = Field(default=None, max_length=200)
    componentes: Optional[str] = Field(default=None, max_length=20)
    componente_extra: Optional[str] = Field(default=None, max_length=300)
    alcance: Optional[str] = Field(default=None, max_length=50)
    area_efeito: Optional[str] = Field(default=None, max_length=100)
    duracao: Optional[str] = Field(default=None, max_length=100)
    tempo_conjuracao: Optional[str] = Field(default=None, max_length=50)
    dano: Optional[str] = Field(default=None, max_length=50)
    teste_resistencia: Optional[str] = Field(default=None, max_length=50)
    resistencia_magica: bool = False
    resistencia_magia_texto: Optional[str] = Field(default=None, max_length=50)
    descricao: str = Field(..., min_length=1, max_length=1000)
    descricao_en: Optional[str] = Field(default=None, max_length=1000)
    e_magia_dominio: bool = False
    dominios: Optional[str] = Field(default=None, max_length=250)
    pagina_referencia: Optional[int] = Field(default=None, ge=1)
    classes_niveis: List[MagiaClasseNivel] = Field(default_factory=list, min_length=1)

    @model_validator(mode="after")
    def validar_magia_dominio(self):
        if self.e_magia_dominio and not (self.dominios and self.dominios.strip()):
            raise ValueError("Para magia de domínio, informe ao menos um domínio")
        return self


class MagiaUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=100)
    nome_en: Optional[str] = Field(default=None, max_length=100)
    escola: Optional[str] = Field(default=None, min_length=1, max_length=50)
    sub_escola: Optional[str] = Field(default=None, max_length=50)
    descritor: Optional[str] = Field(default=None, max_length=200)
    componentes: Optional[str] = Field(default=None, max_length=20)
    componente_extra: Optional[str] = Field(default=None, max_length=300)
    alcance: Optional[str] = Field(default=None, max_length=50)
    area_efeito: Optional[str] = Field(default=None, max_length=100)
    duracao: Optional[str] = Field(default=None, max_length=100)
    tempo_conjuracao: Optional[str] = Field(default=None, max_length=50)
    dano: Optional[str] = Field(default=None, max_length=50)
    teste_resistencia: Optional[str] = Field(default=None, max_length=50)
    resistencia_magica: Optional[bool] = None
    resistencia_magia_texto: Optional[str] = Field(default=None, max_length=50)
    descricao: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    descricao_en: Optional[str] = Field(default=None, max_length=1000)
    e_magia_dominio: Optional[bool] = None
    dominios: Optional[str] = Field(default=None, max_length=250)
    pagina_referencia: Optional[int] = Field(default=None, ge=1)
    classes_niveis: Optional[List[MagiaClasseNivel]] = None
    ativo: Optional[bool] = None


class MagiaResponse(MagiaBase):
    """Schema de resposta — inclui campos gerados pelo banco"""

    id: int
    eh_truque: bool
    tem_dano: bool
    classes_niveis: List[MagiaClasseNivelResponse] = []
    data_criacao: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (era orm_mode no v1)


class MagiaFiltro(BaseModel):
    """Schema para filtros de busca de magias"""

    classe: Optional[str] = Field(default=None, max_length=50)
    nivel: Optional[int] = None
    escola: Optional[str] = Field(default=None, max_length=50)
    nome: Optional[str] = Field(default=None, max_length=100)
    ativo: Optional[bool] = None


class MagiaImportErro(BaseModel):
    linha: int = Field(..., ge=2)
    campo: str = Field(..., min_length=1, max_length=100)
    mensagem: str = Field(..., min_length=1, max_length=300)


class MagiaImportPreviewItem(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    nome_en: Optional[str] = Field(default=None, max_length=100)
    escola: str = Field(..., min_length=1, max_length=50)
    sub_escola: Optional[str] = Field(default=None, max_length=50)
    descritor: Optional[str] = Field(default=None, max_length=200)
    componentes: Optional[str] = Field(default=None, max_length=20)
    componente_extra: Optional[str] = Field(default=None, max_length=300)
    alcance: Optional[str] = Field(default=None, max_length=50)
    area_efeito: Optional[str] = Field(default=None, max_length=100)
    duracao: Optional[str] = Field(default=None, max_length=100)
    tempo_conjuracao: Optional[str] = Field(default=None, max_length=50)
    dano: Optional[str] = Field(default=None, max_length=50)
    teste_resistencia: Optional[str] = Field(default=None, max_length=50)
    resistencia_magica: bool = False
    resistencia_magia_texto: Optional[str] = Field(default=None, max_length=50)
    descricao: str = Field(..., min_length=1, max_length=1000)
    descricao_en: Optional[str] = Field(default=None, max_length=1000)
    e_magia_dominio: bool = False
    dominios: Optional[str] = Field(default=None, max_length=250)
    pagina_referencia: Optional[int] = Field(default=None, ge=1)
    classes_niveis: List[MagiaClasseNivel] = Field(default_factory=list, min_length=1)


class MagiaImportPreviewResponse(BaseModel):
    import_id: str
    total_linhas: int = Field(..., ge=0)
    validas: int = Field(..., ge=0)
    invalidas: int = Field(..., ge=0)
    preview: List[MagiaImportPreviewItem] = Field(default_factory=list)
    erros: List[MagiaImportErro] = Field(default_factory=list)


class MagiaImportConfirmRequest(BaseModel):
    import_id: str = Field(..., min_length=10, max_length=100)


class MagiaImportConfirmResponse(BaseModel):
    importadas: int = Field(..., ge=0)
    falhas: int = Field(..., ge=0)
    erros: List[MagiaImportErro] = Field(default_factory=list)


class MagiaHistoricoResponse(BaseModel):
    id: int
    magia_id: Optional[int] = None
    usuario_id: Optional[int] = None
    acao: str
    dados_anteriores: Optional[dict] = None
    dados_novos: Optional[dict] = None
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True
