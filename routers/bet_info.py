"""
OMCs are Oil Marketing Companies
"""
import asyncio
from threading import Thread
from typing import List

from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks

from dependencies.data import query_bet_infos, query_bet_info, create_bet_info, get_authenticated_user
from load_predictions import load
from models import BetInfoInDB, User

router = APIRouter(
    prefix='/bet_info',
    tags=['BetInfo']
)


@router.get("/", response_model=List[BetInfoInDB])
async def get_bet_infos(user: User = Depends(get_authenticated_user),
                        bet_info: List[BetInfoInDB] = Depends(query_bet_infos)):
    return bet_info


@router.get("/{id}")
async def get_bet_info(user: User = Depends(get_authenticated_user), bet_info: BetInfoInDB = Depends(query_bet_info)):
    return bet_info


@router.post("/", response_model=BetInfoInDB)
async def create_get_bet_info(user: User = Depends(get_authenticated_user),
                              bet_info: BetInfoInDB = Depends(create_bet_info)):
    return bet_info


@router.get("/update_bet_info/")
async def update_bet_info(background_tasks: BackgroundTasks, user: User = Depends(get_authenticated_user)):
    background_tasks.add_task(load)
    return {"detail": "request accepted for processing"}
