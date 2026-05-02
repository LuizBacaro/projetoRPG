"""Auth Hub multi-jogo — catálogo de jogos e memberships."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.shared.core.database import get_db
from app.shared.repositories.game_repository import (
    GameRepository,
    UserGameMembershipRepository,
)
from app.shared.services.game_service import GameService


def get_game_repository(db: Session = Depends(get_db)) -> GameRepository:
    return GameRepository(db)


def get_user_game_membership_repository(
    db: Session = Depends(get_db),
) -> UserGameMembershipRepository:
    return UserGameMembershipRepository(db)


def get_game_service(
    games: GameRepository = Depends(get_game_repository),
    memberships: UserGameMembershipRepository = Depends(
        get_user_game_membership_repository
    ),
) -> GameService:
    return GameService(games, memberships)
