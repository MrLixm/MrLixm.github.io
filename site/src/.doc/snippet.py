from pathlib import Path
import OpenImageIO as oiio


def read_image(path: Path) -> oiio.ImageBuf:
    """
    Read given image from disk as oiio buffer.
    """
    return oiio.ImageBuf(str(path))
