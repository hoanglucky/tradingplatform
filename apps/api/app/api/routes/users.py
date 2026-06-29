from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import MvpUserRead
from app.services.mvp_user import get_mvp_user

router = APIRouter()


@router.get("/me", response_model=MvpUserRead)
async def get_current_user(user: User = Depends(get_mvp_user)) -> MvpUserRead:
    return MvpUserRead.model_validate(user)
