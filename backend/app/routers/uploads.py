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
}


def _has_valid_magic(content_type: str, header: bytes) -> bool:
    if content_type in ALLOWED_IMAGE_TYPES:
        if any(header[: len(sig)] == sig for sig in _IMAGE_MAGIC_BYTES):
            return True
        return header[:4] == b"RIFF" and header[8:12] == b"WEBP"
    if content_type in ALLOWED_VIDEO_TYPES:
        return header[4:8] == b"ftyp" or header[:4] == b"\x1a\x45\xdf\xa3"
    if content_type in ALLOWED_DOC_TYPES:
        return header[:4] == b"%PDF"
    return False


async def _save_file(file: UploadFile, subfolder: str, allowed_types: set, max_size: int) -> str:
    from app.services.media_sanitize_service import sanitize_file

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
    header = await file.read(16)
    await file.seek(0)
    if not _has_valid_magic(file.content_type, header):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match file type",
        )
    ext = Path(file.filename or "file").suffix.lower() or ".bin"
    if ext in {".html", ".htm", ".svg", ".js", ".php", ".phtml"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension not allowed",
        )
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = folder / filename
    tmp_path = folder / f"{filename}.part"
    total = 0
    with tmp_path.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_size:
                tmp_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large (max {max_size // (1024 * 1024)}MB)",
                )
            f.write(chunk)
    try:
        sanitize_file(tmp_path, file.content_type)
    except HTTPException:
        tmp_path.unlink(missing_ok=True)
        raise
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File could not be processed")
    tmp_path.replace(file_path)
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
