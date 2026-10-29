"""Router for profile wall publications (microblogging).

Top-level posts live on a user wall (``/users/{id}/posts/``) or a festival
wall (``/festivals/{id}/posts/``). Replies nest under ``/posts/{id}/replies/``
and require the parent to allow replies. Moderation (pin/hide/lock replies)
is restricted to central admins, festival management/organizers, and users
holding a festival moderator role.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.enums import UserRoleStatus
from app.models.festival import Festival
from app.models.post import Post
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.routers.dependencies import get_current_user_optional, get_or_404
from app.routers.permissions import can_manage_festival, is_admin
from app.schemas.post import PostCreate, PostModerate, PostResponse, PostsPage, PostUpdate
from app.services.post_service import PostService

router = APIRouter()

post_service = PostService()

MODERATOR_ROLE_NAMES = {"moderator", "moderador", "moderadora", "mod", "moderacion", "moderation"}
ACTIVE_STATUSES = {UserRoleStatus.ACTIVE.value, UserRoleStatus.APPROVED.value}


def _is_festival_moderator(db: Session, user_id: int, festival_id: int) -> bool:
    return (
        db.query(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.name.in_(MODERATOR_ROLE_NAMES),
            UserRole.status.in_(ACTIVE_STATUSES),
            (UserRole.festival_id == festival_id) | (UserRole.festival_id.is_(None)),
        )
        .first()
        is not None
    )


def _can_moderate_scope(db: Session, user: User, post: Post) -> bool:
    if is_admin(user):
        return True
    if post.festival_id is not None:
        if can_manage_festival(db, user, post.festival_id):
            return True
        return _is_festival_moderator(db, user.id, post.festival_id)
    if post.target_user_id is not None:
        return user.id == post.target_user_id
    if post.parent_post_id is not None:
        parent = post_service.get(db, post.parent_post_id)
        if parent is not None:
            return _can_moderate_scope(db, user, parent)
    return False


def _can_view_hidden(db: Session, user: User | None, post: Post) -> bool:
    if not post.is_hidden:
        return True
    if user is None:
        return False
    if user.id == post.author_id:
        return True
    return _can_moderate_scope(db, user, post)


def _to_response(db: Session, post: Post) -> PostResponse:
    data = PostResponse.model_validate(post)
    data.reply_count = post_service.reply_count(db, post.id)
    return data


@router.get("/users/{user_id}/posts/", response_model=PostsPage)
async def list_user_posts(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    get_or_404(db, User, user_id, "User")
    include_hidden = current_user is not None and (is_admin(current_user) or current_user.id == user_id)
    result = post_service.list_user_wall(db, user_id, page, size, include_hidden=include_hidden)
    items = [_to_response(db, p) for p in result["items"] if _can_view_hidden(db, current_user, p)]
    return {**result, "items": items}


@router.post("/users/{user_id}/posts/", response_model=PostResponse, status_code=201)
async def create_user_post(
    user_id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    created = post_service.create_wall_post(db, post, author_id=current_user.id, target_user_id=user_id)
    return _to_response(db, created)


@router.get("/festivals/{festival_id}/posts/", response_model=PostsPage)
async def list_festival_posts(
    festival_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    get_or_404(db, Festival, festival_id, "Festival")
    include_hidden = current_user is not None and (
        is_admin(current_user) or can_manage_festival(db, current_user, festival_id)
    )
    result = post_service.list_festival_wall(db, festival_id, page, size, include_hidden=include_hidden)
    items = [_to_response(db, p) for p in result["items"] if _can_view_hidden(db, current_user, p)]
    return {**result, "items": items}


@router.post("/festivals/{festival_id}/posts/", response_model=PostResponse, status_code=201)
async def create_festival_post(
    festival_id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, Festival, festival_id, "Festival")
    created = post_service.create_wall_post(db, post, author_id=current_user.id, festival_id=festival_id)
    return _to_response(db, created)


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    post = get_or_404(db, Post, post_id, "Post")
    if not _can_view_hidden(db, current_user, post):
        raise HTTPException(status_code=404, detail="Post not found")
    return _to_response(db, post)


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Post, post_id, "Post")
    if existing.author_id != current_user.id and not _can_moderate_scope(db, current_user, existing):
        raise HTTPException(status_code=403, detail="Not allowed to edit this post")
    updated = post_service.update(db, post_id, post)
    return _to_response(db, updated)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Post, post_id, "Post")
    if existing.author_id != current_user.id and not _can_moderate_scope(db, current_user, existing):
        raise HTTPException(status_code=403, detail="Not allowed to delete this post")
    post_service.delete(db, post_id)
    return {"message": "Post deleted"}


@router.get("/posts/{post_id}/replies/", response_model=PostsPage)
async def list_replies(
    post_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    get_or_404(db, Post, post_id, "Post")
    result = post_service.list_replies(db, post_id, page, size)
    items = [_to_response(db, p) for p in result["items"] if _can_view_hidden(db, current_user, p)]
    return {**result, "items": items}


@router.post("/posts/{post_id}/replies/", response_model=PostResponse, status_code=201)
async def create_reply(
    post_id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parent = get_or_404(db, Post, post_id, "Post")
    if not parent.allow_replies and not _can_moderate_scope(db, current_user, parent):
        raise HTTPException(status_code=403, detail="Replies are disabled for this post")
    created = post_service.create_wall_post(
        db,
        post,
        author_id=current_user.id,
        target_user_id=parent.target_user_id,
        festival_id=parent.festival_id,
        parent_post_id=parent.id,
    )
    return _to_response(db, created)


@router.post("/posts/{post_id}/moderate", response_model=PostResponse)
async def moderate_post(
    post_id: int,
    moderation: PostModerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Post, post_id, "Post")
    if not _can_moderate_scope(db, current_user, existing):
        raise HTTPException(status_code=403, detail="Not allowed to moderate this post")
    update_data = moderation.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)
    db.commit()
    db.refresh(existing)
    return _to_response(db, existing)
