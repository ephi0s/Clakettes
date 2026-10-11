"""Strip identifying metadata from uploaded audiovisual files (RGPD art. 5/25).

Covered: images (EXIF/XMP, incl. GPS), MP4/MOV tags, WebM tags, PDF document
info. Videos prefer ``ffmpeg -map_metadata -1 -c copy`` when available and
fall back to mutagen for MP4/MOV; WebM without ffmpeg is rejected (fail
closed) instead of storing tagged files.
"""

import io
import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
DOC_TYPES = {"application/pdf"}


def _strip_image(path: Path) -> None:
    from PIL import Image, ImageOps

    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        fmt = (img.format or "").upper()
        buf = io.BytesIO()
        if fmt in ("JPEG", "JPG", "MPO"):
            rgb = img.convert("RGB") if img.mode in ("RGBA", "LA", "P") else img
            rgb.save(buf, format="JPEG", quality=95)
        elif fmt == "PNG":
            img.save(buf, format="PNG")
        elif fmt == "WEBP":
            img.save(buf, format="WEBP", quality=95)
        elif fmt == "GIF":
            img.save(buf, format="GIF")
        else:
            img.save(buf, format=fmt or "PNG")
    path.write_bytes(buf.getvalue())


def _strip_video_ffmpeg(path: Path) -> bool:
    if not shutil.which("ffmpeg"):
        return False
    tmp = path.with_suffix(path.suffix + ".clean")
    try:
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(path),
                "-map_metadata",
                "-1",
                "-c",
                "copy",
                str(tmp),
            ],
            capture_output=True,
            timeout=300,
        )
        if proc.returncode != 0 or not tmp.is_file():
            logger.warning("ffmpeg metadata strip failed for %s", path.name)
            return False
        tmp.replace(path)
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("ffmpeg unavailable for %s: %s", path.name, exc)
        return False
    finally:
        if tmp.is_file() and tmp.stat().st_size == 0:
            tmp.unlink(missing_ok=True)


def _strip_video_mutagen(path: Path, content_type: str) -> None:
    if content_type in ("video/mp4", "video/quicktime"):
        from mutagen.mp4 import MP4

        media = MP4(str(path))
        if media.tags:
            media.delete()
    else:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="WebM uploads require ffmpeg for metadata removal",
        )


def _strip_video(path: Path, content_type: str) -> None:
    if _strip_video_ffmpeg(path):
        return
    if shutil.which("ffmpeg"):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Video metadata could not be removed",
        )
    logger.warning("ffmpeg not found, using mutagen fallback for %s", path.name)
    _strip_video_mutagen(path, content_type)


def _strip_pdf(path: Path) -> None:
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({})
    with path.open("wb") as f:
        writer.write(f)


def sanitize_file(path: Path, content_type: str) -> None:
    """Remove identifying metadata from a stored upload, in place."""
    if content_type in IMAGE_TYPES:
        _strip_image(path)
    elif content_type in VIDEO_TYPES:
        _strip_video(path, content_type)
    elif content_type in DOC_TYPES:
        _strip_pdf(path)
