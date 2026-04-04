"""
Exceções customizadas da aplicação
"""


class ArenaBaseException(Exception):
    """Exceção base para todas as exceções customizadas"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class CombatenteNotFoundError(ArenaBaseException):
    """Exceção quando combatente não é encontrado"""
    def __init__(self, message: str = "Combatente não encontrado"):
        super().__init__(message, status_code=404)


class CombateNotFoundError(ArenaBaseException):
    """Exceção quando combate não é encontrado"""
    def __init__(self, message: str = "Combate não encontrado"):
        super().__init__(message, status_code=404)


class CombateJaAtivoError(ArenaBaseException):
    """Exceção quando já existe combate ativo"""
    def __init__(self, message: str = "Já existe um combate ativo"):
        super().__init__(message, status_code=400)


class CombateFinalizadoError(ArenaBaseException):
    """Exceção quando combate está finalizado"""
    def __init__(self, message: str = "Combate finalizado"):
        super().__init__(message, status_code=400)


class ConcurrencyConflictError(ArenaBaseException):
    """Exceção para conflito de concorrência por versão de combate desatualizada."""

    def __init__(self, message: str = "Conflito de concorrência no combate"):
        super().__init__(message, status_code=409)


class InvalidHPError(ArenaBaseException):
    """Exceção para valores de HP inválidos"""
    def __init__(self, message: str = "Valor de HP inválido"):
        super().__init__(message, status_code=400)


class InvalidFileError(ArenaBaseException):
    """Exceção para arquivos inválidos"""
    def __init__(self, message: str = "Arquivo inválido"):
        super().__init__(message, status_code=400)
        
class DadosInvalidos(ArenaBaseException):
    """Exceção para dados inválidos"""
    def __init__(self, mensagem: str = "Dados inválidos"):
        super().__init__(
            message=mensagem,
            status_code=400
        )


class CombatenteNaoEncontrado(ArenaBaseException):
    """Exceção quando combatente não é encontrado"""
    def __init__(self, combatente_id: int):
        super().__init__(
            message=f"Combatente com ID {combatente_id} não encontrado",
            status_code=404
        )