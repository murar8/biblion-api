import uuid
from datetime import datetime, timedelta
from functools import reduce
from http import HTTPStatus
from urllib.parse import urljoin

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo import ReturnDocument
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.access_token import AccessToken
from app.config import Config
from app.email_service import EmailService
from app.providers.access_token import get_access_token
from app.providers.config import get_config
from app.providers.database import get_database
from app.providers.email_service import get_email_service
from app.providers.logged_user import get_logged_user

from .request import (
    CreateUserRequest,
    LoginUserRequest,
    ResetPasswordRequest,
    UpdateUserRequest,
)
from .response import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: dict[str, any] = Depends(get_logged_user)):
    return UserResponse.from_mongo(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, database: Database = Depends(get_database)):
    user = await database.users.find_one({"_id": user_id})

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return UserResponse.from_mongo(user)


@router.post("/", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def create_user(
    body: CreateUserRequest,
    database: Database = Depends(get_database),
):
    created_at = datetime.utcnow()
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(body.password.encode(), salt)

    document = {
        "_id": uuid.uuid4(),
        "email": body.email,
        "passwordHash": password_hash,
        "verified": False,
        "createdAt": created_at,
        "updatedAt": created_at,
    }

    if body.name:
        document["name"] = body.name

    try:
        result = await database.users.insert_one(document=document)
    except DuplicateKeyError as exc:
        key, value = list(exc.details["keyValue"].items())[0]
        detail = f"An user with {key} '{value}' already exists."
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=detail) from exc

    user = await database.users.find_one({"_id": result.inserted_id})

    return UserResponse.from_mongo(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    body: UpdateUserRequest,
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
):
    if user_id != jwt.sub:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    data = body.dict(exclude_unset=True)
    to_set = {"updatedAt": datetime.utcnow()}
    to_unset = {}

    if "name" in data:
        if data["name"]:
            to_set["name"] = data["name"]
        else:
            to_unset["name"] = None

    if "email" in data:
        to_set["email"] = data["email"]
        to_set["verified"] = False

    try:
        user = await database.users.find_one_and_update(
            {"_id": user_id},
            {"$set": to_set, "$unset": to_unset},
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError as exc:
        key, value = list(exc.details["keyValue"].items())[0]
        detail = f"An user with {key} '{value}' already exists."
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=detail) from exc

    return UserResponse.from_mongo(user)


@router.post("/login", response_model=UserResponse)
async def login_user(
    body: LoginUserRequest,
    response: Response,
    database: Database = Depends(get_database),
    config: Config = Depends(get_config),
):
    find = [{"email": body.email}]

    if body.name:
        find.append({"name": body.name})

    user = await database.users.find_one({"$or": find})

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if not bcrypt.checkpw(body.password.encode(), user["passwordHash"]):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    response.set_cookie(
        key="access_token",
        value=AccessToken.encode(user["_id"], config.jwt),
        secure=True,
        httponly=True,
        max_age=config.jwt.expiration,
    )

    return UserResponse.from_mongo(user)


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout_user(response: Response):
    response.set_cookie(
        key="access_token",
        value=None,
        secure=True,
        httponly=True,
        expires=datetime.now(),
    )


@router.post("/verify", status_code=HTTPStatus.NO_CONTENT)
async def request_email_verification(
    database: Database = Depends(get_database),
    config: Config = Depends(get_config),
    email_service: EmailService = Depends(get_email_service),
    user: dict[str, any] = Depends(get_logged_user),
):
    verification_code = uuid.uuid4()

    content = {
        "verificationCode": verification_code,
        "verificationCodeIat": datetime.now(),
    }

    await database.users.update_one({"_id": user["_id"]}, {"$set": content})

    template_variables = {
        "title": "Email Confirmation",
        "description": "Confirm Your Email Address.",
        "base_url": config.website.base_url,
        "confirmation_url": reduce(
            urljoin, [config.website.base_url, "verify/", str(verification_code)]
        ),
    }

    email_service.send_email(
        subject="Verify your address",
        to=user["email"],
        template="account-action.html",
        variables=template_variables,
    )


@router.post("/verify/{code}", response_model=UserResponse)
async def verify_email(
    code: uuid.UUID,
    database: Database = Depends(get_database),
    user: dict[str, any] = Depends(get_logged_user),
    config: Config = Depends(get_config),
):
    if "verificationCode" not in user or "verificationCodeIat" not in user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No account verification requests found.",
        )

    expiration_delta = timedelta(0, config.email.verification_expiration)
    expiration = user["verificationCodeIat"] + expiration_delta

    if expiration < datetime.now():
        raise HTTPException(
            status_code=HTTPStatus.GONE, detail="Verification code has expired."
        )

    if user["verificationCode"] != code:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Verification code is invalid."
        )

    user = await database.users.find_one_and_update(
        {"_id": user["_id"]},
        {
            "$set": {"verified": True, "updatedAt": datetime.now()},
            "$unset": {"verificationCode": "", "verificationCodeIat": ""},
        },
        return_document=ReturnDocument.AFTER,
    )

    return UserResponse.from_mongo(user)


@router.post("/password-reset", status_code=HTTPStatus.NO_CONTENT)
async def request_password_reset(
    database: Database = Depends(get_database),
    config: Config = Depends(get_config),
    email_service: EmailService = Depends(get_email_service),
    user: dict[str, any] = Depends(get_logged_user),
):
    reset_code = uuid.uuid4()

    content = {
        "resetCode": reset_code,
        "resetCodeIat": datetime.now(),
    }

    await database.users.update_one({"_id": user["_id"]}, {"$set": content})

    template_variables = {
        "title": "Password Reset",
        "description": "Reset your password.",
        "base_url": config.website.base_url,
        "confirmation_url": reduce(
            urljoin, [config.website.base_url, "reset/", str(reset_code)]
        ),
    }

    email_service.send_email(
        subject="Password Reset",
        to=user["email"],
        template="account-action.html",
        variables=template_variables,
    )


@router.post("/password-reset/{code}", status_code=HTTPStatus.NO_CONTENT)
async def reset_password(
    code: uuid.UUID,
    body: ResetPasswordRequest,
    response: Response,
    database: Database = Depends(get_database),
    user: dict[str, any] = Depends(get_logged_user),
    config: Config = Depends(get_config),
):
    if "resetCode" not in user or "resetCodeIat" not in user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No password reset requests found.",
        )

    expiration_delta = timedelta(0, config.email.password_reset_expiration)
    expiration = user["resetCodeIat"] + expiration_delta

    if expiration < datetime.now():
        raise HTTPException(
            status_code=HTTPStatus.GONE, detail="Reset code has expired."
        )

    if user["resetCode"] != code:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Reset code is invalid."
        )

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(body.password.encode(), salt)
    updated_at = datetime.now()

    await database.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"passwordHash": password_hash, "updatedAt": updated_at},
            "$unset": {"resetCode": "", "resetCodeIat": ""},
        },
    )

    response.set_cookie(
        key="access_token",
        value=None,
        secure=True,
        httponly=True,
        expires=datetime.now(),
    )
