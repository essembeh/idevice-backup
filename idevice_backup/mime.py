import mimetypes
from pathlib import Path

mimetypes.init()


def get_mime(file: Path) -> str | None:
    """
    Return the mime of a file
    """
    mime, _ = mimetypes.guess_type(file)
    return mime


def is_video(file: Path) -> bool:
    """
    check if given file is a video
    """
    mime = get_mime(file)
    return mime is not None and mime.startswith("video/")


def is_image(file: Path) -> bool:
    """
    check if given file is an image
    """
    mime = get_mime(file)
    return mime is not None and mime.startswith("image/")
