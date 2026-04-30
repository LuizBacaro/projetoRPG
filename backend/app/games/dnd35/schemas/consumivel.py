from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConsumivelBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=600)
    pagina_referencia: Optional[str] = Field(default=None, max_length=50)
    categoria: Optional[str] = Field(default=None, max_length=60)
    tipo: Optional[str] = Field(default=None, max_length=60)
    custo: Optional[str] = Field(default=None, max_length=50)
    peso: Optional[str] = Field(default=None, max_length=30)
    ativo: bool = True


class ConsumivelCreate(ConsumivelBase):
    pass


class ConsumivelResponse(ConsumivelBase):
    id: int
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsumivelJogadorCreate(BaseModel):
    consumivel_id: int
    quantidade: int = Field(default=1, ge=1, le=999)


class ConsumivelJogadorListResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    pagina_referencia: Optional[str] = None
    categoria: Optional[str] = None
    tipo: Optional[str] = None
    custo: Optional[str] = None
    peso: Optional[str] = None
    quantidade: int

    class Config:
        from_attributes = True
