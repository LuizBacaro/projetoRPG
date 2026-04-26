"""
API v1 Router aggregator
"""
from fastapi import APIRouter
from . import combatentes, combate

api_router = APIRouter()
api_router.include_router(combatentes.router)
api_router.include_router(combate.router)
