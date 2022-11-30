import uuid
from datetime import datetime, timedelta
from functools import reduce
from http import HTTPStatus
from urllib.parse import urljoin

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.database import Database

from app.providers.access_token import get_access_token
from app.providers.config import get_config
from app.providers.database import get_database
from app.providers.email_service import get_email_service
from app.providers.logged_user import get_logged_user
from app.users.request import CreateUserRequest, LoginUserRequest, UpdateUserRequest
from app.users.response import UserResponse
from app.util.access_token import AccessToken
from app.util.config import Config
from app.util.email_service import EmailService

router = APIRouter()


@router.get("/{uid}", response_model=UserResponse)
async def get_user(uid: str, database: Database = Depends(get_database)):
    user = await database.users.find_one({"_id": uuid.UUID(uid)})

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return UserResponse.from_mongo(user)


@router.post("/", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def create_user(
    body: CreateUserRequest,
    database: Database = Depends(get_database),
):
    user = await database.users.find_one(
        {"$or": [{"email": body.email}, {"name": body.name}]}
    )

    if user:
        raise HTTPException(status_code=HTTPStatus.CONFLICT)

    created_at = datetime.utcnow()
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(body.password.encode(), salt)

    document = {
        "_id": uuid.uuid4(),
        "email": body.email,
        "name": body.name,
        "password_hash": password_hash,
        "verified": False,
        "createdAt": created_at,
        "updatedAt": created_at,
    }

    res = await database.users.insert_one(document=document)
    user = await database.users.find_one({"_id": res.inserted_id})

    return UserResponse.from_mongo(user)


@router.patch("/{uid}", response_model=UserResponse)
async def update_user(
    uid: str,
    body: UpdateUserRequest,
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
):
    if uid != jwt.sub:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    document = {"updatedAt": datetime.utcnow()}

    if body.name:
        document["name"] = body.name

    if body.email:
        document["email"] = body.email
        document["verified"] = False

    if body.password:
        salt = bcrypt.gensalt()
        document["password_hash"] = bcrypt.hashpw(body.password.encode(), salt)

    result = await database.users.update_one(
        {"_id": uuid.UUID(uid)}, {"$set": document}
    )

    if not result.matched_count:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    user = await database.users.find_one({"_id": uuid.UUID(uid)})
    return UserResponse.from_mongo(user)


@router.post("/login", response_model=UserResponse)
async def login_user(
    body: LoginUserRequest,
    response: Response,
    database: Database = Depends(get_database),
    config: Config = Depends(get_config),
):
    user = await database.users.find_one(
        {"$or": [{"email": body.email}, {"name": body.name}]}
    )

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if not bcrypt.checkpw(body.password.encode(), user["password_hash"]):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    response.set_cookie(
        key="access_token",
        value=AccessToken.encode(str(user["_id"]), config.jwt),
        secure=True,
        httponly=True,
        max_age=config.jwt.expiration,
    )

    return UserResponse.from_mongo(user)


@router.post("/verification-code", status_code=HTTPStatus.NO_CONTENT)
async def request_verification_code(
    database: Database = Depends(get_database),
    config: Config = Depends(get_config),
    email_service: EmailService = Depends(get_email_service),
    user: dict = Depends(get_logged_user),
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


@router.post("/verify/{code}", status_code=HTTPStatus.NO_CONTENT)
async def verify_user(
    code: str,
    database: Database = Depends(get_database),
    user=Depends(get_logged_user),
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

    if user["verificationCode"] != uuid.UUID(code):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Verification code is invalid."
        )

    await database.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"verified": True},
            "$unset": {"verificationCode": "", "verificationCodeIat": ""},
        },
    )
