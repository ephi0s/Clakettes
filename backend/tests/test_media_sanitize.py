"""Tests for audiovisual metadata stripping (RGPD art. 5/25)."""

import io

import pytest
from fastapi import HTTPException
from PIL import Image
from pypdf import PdfReader, PdfWriter

from app.services import media_sanitize_service as sanitize


def _jpeg_with_exif(path):
    img = Image.new("RGB", (16, 32), "blue")
    exif = Image.Exif()
    exif[0x010F] = "Camera Maker"
    exif[0x0110] = "Model X"
    exif[0x0132] = "2026:10:11 12:00:00"
    exif[0x8825] = {0: b"\x02\x03\x00\x00", 1: "N", 2: (40.0, 7.0, 0.0), 3: "W", 4: (3.0, 41.0, 0.0)}
    exif[0x0112] = 6
    img.save(path, format="JPEG", exif=exif)


def _png_with_text(path):
    from PIL.PngImagePlugin import PngInfo

    img = Image.new("RGB", (8, 8), "green")
    info = PngInfo()
    info.add_text("Author", "John Doe")
    info.add_text("GPS", "40.0,-3.7")
    img.save(path, format="PNG", pnginfo=info)


def _pdf_with_meta(path):
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.add_metadata({"/Author": "John Doe", "/Title": "Secret"})
    with open(path, "wb") as f:
        writer.write(f)


class TestStripImage:
    def test_jpeg_exif_removed(self, tmp_path):
        target = tmp_path / "a.jpg"
        _jpeg_with_exif(target)
        assert Image.open(target).getexif()
        sanitize.sanitize_file(target, "image/jpeg")
        assert not Image.open(target).getexif()

    def test_png_text_chunks_removed(self, tmp_path):
        target = tmp_path / "a.png"
        _png_with_text(target)
        assert Image.open(target).info.get("Author") == "John Doe"
        sanitize.sanitize_file(target, "image/png")
        assert "Author" not in Image.open(target).info


class TestStripPdf:
    def test_pdf_info_removed(self, tmp_path):
        target = tmp_path / "a.pdf"
        _pdf_with_meta(target)
        assert PdfReader(str(target)).metadata.author == "John Doe"
        sanitize.sanitize_file(target, "application/pdf")
        assert PdfReader(str(target)).metadata.author in (None, "")


class TestStripVideo:
    def test_webm_without_ffmpeg_is_rejected(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sanitize.shutil, "which", lambda _: None)
        target = tmp_path / "a.webm"
        target.write_bytes(b"\x1a\x45\xdf\xa3" + b"\x00" * 64)
        with pytest.raises(HTTPException) as exc:
            sanitize.sanitize_file(target, "video/webm")
        assert exc.value.status_code == 422

    def test_mp4_tags_removed_with_mutagen(self, tmp_path, monkeypatch):
        from mutagen.mp4 import MP4

        monkeypatch.setattr(sanitize.shutil, "which", lambda _: None)
        target = tmp_path / "a.mp4"
        target.write_bytes(_minimal_mp4())
        media = MP4(str(target))
        media["\xa9too"] = ["Lavf"]
        media["\xa9xyz"] = ["40.0/-3.7"]
        media.save()
        sanitize.sanitize_file(target, "video/mp4")
        assert not MP4(str(target)).tags


class TestUploadEndpoint:
    def test_avatar_exif_stripped_on_upload(self, client, auth_headers, tmp_path, monkeypatch):
        headers, _ = auth_headers
        monkeypatch.chdir(tmp_path)
        src = tmp_path / "me.jpg"
        _jpeg_with_exif(src)
        with open(src, "rb") as f:
            response = client.post(
                "/api/uploads/avatar",
                headers=headers,
                files={"file": ("me.jpg", f, "image/jpeg")},
            )
        assert response.status_code == 200
        stored = tmp_path / "uploads" / response.json()["url"].split("/uploads/")[1]
        assert not Image.open(stored).getexif()

    def test_upload_rejects_bad_magic(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/uploads/avatar",
            headers=headers,
            files={"file": ("x.png", io.BytesIO(b"not an image at all"), "image/png")},
        )
        assert response.status_code == 400


def _box(typ: bytes, payload: bytes) -> bytes:
    import struct

    return struct.pack(">I", 8 + len(payload)) + typ + payload


def _minimal_mp4() -> bytes:
    import struct

    mvhd = _box(b"mvhd", struct.pack(">IIIII", 0, 0, 0, 1000, 1000) + b"\x00" * 80)
    mdhd = _box(b"mdhd", struct.pack(">III", 0, 0, 0) + struct.pack(">IIHH", 1000, 1000, 0x55C4, 0))
    hdlr = _box(b"hdlr", struct.pack(">I", 0) + b"vide" + b"\x00" * 12)
    vmhd = _box(b"vmhd", struct.pack(">I", 1))
    dref = _box(b"dref", struct.pack(">II", 0, 1) + _box(b"url ", struct.pack(">I", 1)))
    dinf = _box(b"dinf", dref)
    stsd = _box(b"stsd", struct.pack(">II", 0, 0))
    stts = _box(b"stts", struct.pack(">II", 0, 0))
    stsc = _box(b"stsc", struct.pack(">II", 0, 0))
    stsz = _box(b"stsz", struct.pack(">III", 0, 0, 0))
    stco = _box(b"stco", struct.pack(">II", 0, 0))
    stbl = _box(b"stbl", stsd + stts + stsc + stsz + stco)
    minf = _box(b"minf", vmhd + dinf + stbl)
    mdia = _box(b"mdia", mdhd + hdlr + minf)
    trak = _box(b"trak", _box(b"tkhd", struct.pack(">I", 7) + b"\x00" * 80) + mdia)
    moov = _box(b"moov", mvhd + trak)
    ftyp = _box(b"ftyp", b"isom" + struct.pack(">I", 0) + b"isom")
    return ftyp + moov
