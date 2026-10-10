import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services.user_service import UserService

router = APIRouter()

UPLOAD_DIR = Path("uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_DOC_TYPES = {"application/pdf"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024
MAX_DOC_SIZE = 10 * 1024 * 1024

_IMAGE_MAGIC_BYTES = {
    b"\xff\xd8\xff",
    b"\x89PNG\r\n\x1a\n",
    b"GIF87a",
    b"GIF89a",
    b"RIFF",
}


async def _save_file(file: UploadFile, subfolder: str, allowed_types: set, max_size: int) -> str:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"File type '{file.content_type}' not allowed"
        )
    if file.size is not None and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max {max_size // (1024 * 1024)}MB)",
        )
    folder = UPLOAD_DIR / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    if allowed_types & ALLOWED_IMAGE_TYPES:
        header = await file.read(8)
        await file.seek(0)
        if header[:8] not in _IMAGE_MAGIC_BYTES and allowed_types & ALLOWED_IMAGE_TYPES:
            valid_magic = any(header[: len(sig)] == sig for sig in _IMAGE_MAGIC_BYTES)
            if not valid_magic:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File content does not match image type",
                )
    ext = Path(file.filename or "file").suffix or ".bin"
    filename = f"{uuid.uuid4().hex}{ext}"
    total = 0
    file_path = folder / filename
    with file_path.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_size:
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large (max {max_size // (1024 * 1024)}MB)",
                )
            f.write(chunk)
    return f"/uploads/{subfolder}/{filename}"


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    url = await _save_file(file, "avatars", ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    user_service = UserService()
    user_service.update(db, current_user.id, UserUpdate(avatar_url=url))
    return {"url": url, "user_id": current_user.id}


@router.post("/thumbnail")
async def upload_thumbnail(
    file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    url = await _save_file(file, "thumbnails", ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    return {"url": url}


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    url = await _save_file(file, "videos", ALLOWED_VIDEO_TYPES, MAX_VIDEO_SIZE)
    return {"url": url}


@router.post("/chat-image")
async def upload_chat_image(
    file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    url = await _save_file(file, "chat", ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    return {"url": url}
