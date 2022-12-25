from datetime import datetime, timedelta
from functools import reduce
from http import HTTPStatus
from urllib.parse import urljoin
from uuid import UUID, uuid4

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.errors import DuplicateKeyError

from app.access_token import AccessToken
from app.config import Config
from app.email_service import EmailService
from app.models.database import User
from app.models.users_requests import (
    CreateUserRequest,
    LoginUserRequest,
    ResetPasswordRequest,
    UpdateUserRequest,
)
from app.models.users_responses import UserResponse
from app.providers.config import get_config
from app.providers.email_service import get_email_service
from app.providers.logged_user import get_logged_user

users_router = APIRouter()


@users_router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(get_logged_user)):
    return UserResponse.from_mongo(user)


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    user = await User.get(user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    return UserResponse.from_mongo(user)


@users_router.post("/", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def create_user(
    body: CreateUserRequest,
):
    created_at = datetime.utcnow()
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(body.password.encode(), salt)

    user = User(
        id=uuid4(),
        email=body.email,
        name=body.name,
        passwordHash=password_hash,
        verified=False,
        createdAt=created_at,
        updatedAt=created_at,
    )

    try:
        user = await user.insert()
    except DuplicateKeyError as exc:
        key, value = list(exc.details["keyValue"].items())[0]
        detail = f"A user with '{key}'='{value}' already exists."
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=detail) from exc

    return UserResponse.from_mongo(user)


@users_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID, body: UpdateUserRequest, user: User = Depends(get_logged_user)
):
    if user_id != user.id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    user.updatedAt = datetime.now()

    if body.name is not None:
        user.name = body.name if body.name else None

    if body.email:
        user.email = body.email
        user.verified = False

    try:
        user = await user.save()
    except DuplicateKeyError as exc:
        key, value = list(exc.details["keyValue"].items())[0]
        detail = f"A user with '{key}'='{value}' already exists."
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=detail) from exc

    return UserResponse.from_mongo(user)


@users_router.post("/login", response_model=UserResponse)
async def login_user(
    body: LoginUserRequest,
    response: Response,
    config: Config = Depends(get_config),
):
    user = await User.find_one(
        {"email": body.email} if body.email else {"name": body.name}
    )

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    if not bcrypt.checkpw(body.password.encode(), user.passwordHash):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid password."
        )

    response.set_cookie(
        key="access_token",
        value=AccessToken.encode(user.id, config.jwt),
        secure=True,
        httponly=True,
        max_age=config.jwt.expiration,
    )

    return UserResponse.from_mongo(user)


@users_router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout_user(response: Response):
    # It's safer to set the cookie to an invalid value rather than deleting it.
    # See https://learn.microsoft.com/en-us/previous-versions/aspnet/ms178195(v=vs.100)
    response.set_cookie(
        key="access_token",
        value=None,
        secure=True,
        httponly=True,
        expires=datetime.now(),
    )


@users_router.post("/verify", status_code=HTTPStatus.NO_CONTENT)
async def request_email_verification(
    config: Config = Depends(get_config),
    email_service: EmailService = Depends(get_email_service),
    user: User = Depends(get_logged_user),
):
    user.verificationCode = uuid4()
    user.verificationCodeIat = datetime.now()

    await user.save()

    template_variables = {
        "title": "Email Confirmation",
        "description": "Confirm Your Email Address.",
        "base_url": config.website.base_url,
        "confirmation_url": reduce(
            urljoin, [config.website.base_url, "verify/", str(user.verificationCode)]
        ),
    }

    email_service.send_email(
        subject="Verify your address",
        to=user.email,
        template="account-action.html",
        variables=template_variables,
    )


@users_router.post("/verify/{code}", response_model=UserResponse)
async def verify_email(
    code: UUID,
    user: User = Depends(get_logged_user),
    config: Config = Depends(get_config),
):
    if not user.verificationCode or not user.verificationCodeIat:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No account verification requests found.",
        )

    expiration_delta = timedelta(0, config.email.verification_expiration)
    expiration = user.verificationCodeIat + expiration_delta

    if expiration < datetime.now():
        raise HTTPException(
            status_code=HTTPStatus.GONE, detail="Verification code has expired."
        )

    if user.verificationCode != code:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Verification code is invalid."
        )

    user.verified = True
    user.updatedAt = datetime.now()
    user.verificationCode = None
    user.verificationCodeIat = None

    await user.save()

    return UserResponse.from_mongo(user)


@users_router.post("/password-reset", status_code=HTTPStatus.NO_CONTENT)
async def request_password_reset(
    config: Config = Depends(get_config),
    email_service: EmailService = Depends(get_email_service),
    user: User = Depends(get_logged_user),
):
    user.verificationCode = uuid4()
    user.verificationCodeIat = datetime.now()

    await user.save()

    template_variables = {
        "title": "Password Reset",
        "description": "Reset your password.",
        "base_url": config.website.base_url,
        "confirmation_url": reduce(
            urljoin, [config.website.base_url, "reset/", str(user.resetCode)]
        ),
    }

    email_service.send_email(
        subject="Password Reset",
        to=user.email,
        template="account-action.html",
        variables=template_variables,
    )


@users_router.post("/password-reset/{code}", status_code=HTTPStatus.NO_CONTENT)
async def reset_password(
    code: UUID,
    body: ResetPasswordRequest,
    response: Response,
    user: User = Depends(get_logged_user),
    config: Config = Depends(get_config),
):
    if not user.resetCode or not user.resetCodeIat:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No password reset requests found.",
        )

    expiration_delta = timedelta(0, config.email.password_reset_expiration)
    expiration = user.resetCodeIat + expiration_delta

    if expiration < datetime.now():
        raise HTTPException(
            status_code=HTTPStatus.GONE, detail="Reset code has expired."
        )

    if user.resetCode != code:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Reset code is invalid."
        )

    salt = bcrypt.gensalt()

    user.passwordHash = bcrypt.hashpw(body.password.encode(), salt)
    user.updatedAt = datetime.now()
    user.resetCode = None
    user.resetCodeIat = None

    await user.save()

    response.set_cookie(
        key="access_token",
        value=None,
        secure=True,
        httponly=True,
        expires=datetime.now(),
    )
