from typing import List

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models, auth, database

router = APIRouter(prefix="/posts", tags=["posts"])
cache = TTLCache(maxsize=1000, ttl=300)


@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(request: schemas.PostRequest, current_user: models.User = Depends(auth.get_current_user),
                db: Session = Depends(database.get_db)):
    """
    Creates a new post for the current user.

    This function allows an authenticated user to create a new post by
    providing the post text. The post is saved to the database, and the
    cache for the user's posts is cleared to ensure the next retrieval
    fetches the updated data.

    Args:
        request (schemas.PostRequest): The request data containing the text of the post.
        current_user (models.User): The currently authenticated user making the post.
        db (Session): The database session used to interact with the database.

    Returns:
        models.Post: The newly created post.

    Raises:
        HTTPException: If the user is not authenticated (handled by Depends).
    """
    post = models.Post(text=request.text, user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    cache.pop(current_user.email, None)
    return post


@router.get("/", response_model=List[schemas.PostResponse])
def read_posts(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """
        Retrieves all posts of the current authenticated user.

        This function checks if the user's posts are cached. If they are not
        in the cache, it queries the database for all posts belonging to the
        authenticated user, caches the posts for 5 minutes, and then returns
        them.

        Args:
            current_user (models.User): The currently authenticated user whose posts are to be retrieved.
            db (Session): The database session used to interact with the database.

        Returns:
            List[models.Post]: A list of posts belonging to the current user.

        Raises:
            HTTPException: If the user is not authenticated (handled by Depends).
        """
    if current_user.email in cache:
        return cache[current_user.email]
    posts = db.query(models.Post).filter(models.Post.user_id == int(current_user.id)).all()
    cache[current_user.email] = posts
    return posts


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, current_user: models.User = Depends(auth.get_current_user),
                db: Session = Depends(database.get_db)):
    """
        Deletes a post belonging to the current user.

        This function deletes a specific post based on the provided post ID.
        It ensures that the post belongs to the authenticated user before
        performing the deletion. After the post is deleted, the user's post
        cache is cleared.

        Args:
            post_id (int): The ID of the post to be deleted.
            current_user (models.User): The currently authenticated user who owns the post.
            db (Session): The database session used to interact with the database.

        Returns:
            None: The post is deleted and the response code is 204 (No Content).

        Raises:
            HTTPException: If the post is not found or if it doesn't belong to the authenticated user.
        """
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()
    cache.pop(current_user.email, None)
