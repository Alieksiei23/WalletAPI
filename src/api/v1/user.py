import typing

from api.shema.python_models import (RequestUserModel, RequestUserUpdateModel,
                                     ResponseUserModel, UserModel,)
from core.config import SessionDep
from fastapi import APIRouter, status
from services.user_service import UserService


router = APIRouter()


@router.get("/users",
            response_model=typing.Optional[list[ResponseUserModel]],
            status_code=status.HTTP_200_OK,
            )
async def get_users(session: SessionDep,
                    user_id: typing.Optional[int] = None,
                    email: typing.Optional[str] = None,
                    user_status: typing.Optional[str] = None,
                    ) -> typing.List[ResponseUserModel]:
    result = await UserService.get_users(user_id, email, user_status, session)
    return result


@router.post("/users", status_code=status.HTTP_200_OK)
async def post_user(user: RequestUserModel, session: SessionDep) -> UserModel:
    result = await UserService.register_user(user, session)
    return result


@router.patch("/users/{user_id}", response_model=typing.Optional[UserModel])
async def patch_user(user_id: int, user: RequestUserUpdateModel, session: SessionDep) -> typing.Optional[UserModel]:
    result = await UserService.update_user_status(user_id, user, session)
    return result
