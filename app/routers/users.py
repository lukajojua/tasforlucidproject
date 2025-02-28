from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, auth, database
from app.models import User

router = APIRouter(tags=["users"])


@router.post("/signup", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: schemas.SignupRequest, db: Session = Depends(database.get_db)):
    """
    Registers a new user and returns an access token.

    This function checks if the email is already registered. If not, it
    hashes the password and creates a new user in the database. It then
    generates a JWT access token that expires in 1 hour and returns it to
    the user.

    Args:
        request (schemas.SignupRequest): The request data containing the user's email and password.
        db (Session): The database session to interact with the database.

    Returns:
        dict: A dictionary containing the JWT access token and token type.

    Raises:
        HTTPException: If the email is already registered or an error occurs during the signup process.
    """
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = auth.pwd_context.hash(request.password)
    user = User(email=request.email, hashed_password=hashed_password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during signup process")

    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    """
        Authenticates the user and returns an access token.

        This function checks if the provided email exists and if the password
        is correct. If valid, it generates and returns a JWT access token that
        expires in 1 hour for the authenticated user.

        Args:
            request (schemas.LoginRequest): The request data containing email and password.
            db (Session): The database session to query the user.

        Returns:
            dict: A dictionary containing the JWT access token and token type.

        Raises:
            HTTPException: If the credentials are invalid.
        """
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer"}
