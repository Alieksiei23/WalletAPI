import typing
from fastapi import APIRouter, status

from core.config import SessionDep
from services.user_service import UserService
from src.api.shema.python_models import (ResponseUserModel, RequestUserModel,
                                         UserModel, RequestUserUpdateModel)


router = APIRouter()


@router.get("/users",
            response_model=typing.Optional[list[ResponseUserModel]] | None,
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
async def post_user(user: RequestUserModel, session: SessionDep):
    result = await UserService.register_user(user, session)
    return result


@router.patch("/users/{user_id}", response_model=typing.Optional[UserModel] | None)
async def patch_user(user_id: int, user: RequestUserUpdateModel, session: SessionDep):
    result = await UserService.update_user_status(user_id, user, session)
    return result
