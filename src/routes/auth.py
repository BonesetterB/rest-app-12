from fastapi import APIRouter, HTTPException, Depends, status, Security, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import UserSchema, UserResponseSchema, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email
from fastapi.responses import FileResponse

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema,background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Sign up a new user.

    :param body: User's information.
    :type body: UserSchema
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks
    :param request:  HTTP request.
    :type request: Request
    :param db: The database session.
    :type db: AsyncSession
    :return:  Newly created user.
    :rtype: UserResponseSchema
    """
    try:
        exist_user = await repository_users.get_user_by_email(body.email, db)

        body.password = auth_service.get_password_hash(body.password)
        new_user = await repository_users.create_user(body, db)
        response_user = await repository_users.user_to_response_schema(new_user)
        background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
        return response_user
    except Exception as e:
        if exist_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
        print("Error in signup:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    User login.

    :param body: OAuth2 password request form.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: AsyncSession
    :return: Token model.
    :rtype: TokenModel
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)):
    """
    Refresh access token.

    :param credentials: HTTP authorization credentials.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: AsyncSession
    :return: Token model.
    :rtype: TokenModel
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}




@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm user's email.

    :param token: Email confirmation token.
    :type token: str
    :param db: The database session.
    :type db: AsyncSession
    :return: Сonfirmed users email.
    :rtype: dict
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}



@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Request email confirmation.

    :param body: Request email data.
    :type body: RequestEmail
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks
    :param request: HTTP request.
    :type request: Request
    :param db: The database session.
    :type db: AsyncSession
    :return: Response message.
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}