from __future__ import annotations

import warnings
from dataclasses import dataclass
from io import BytesIO
from typing import Iterable

from PIL import Image, ImageOps, UnidentifiedImageError

from ..config import get_settings


@dataclass(frozen=True)
class TemplateRegion:
    id: str
    left: float
    top: float
    right: float
    bottom: float


@dataclass(frozen=True)
class WorksheetCrop:
    region_id: str
    image_bytes: bytes
    width: int
    height: int


FRACTIONS_V1: tuple[TemplateRegion, ...] = tuple(
    TemplateRegion(
        id=f"p{row * 2 + column + 1}",
        left=0.06 + column * 0.47,
        top=0.17 + row * 0.19,
        right=0.48 + column * 0.47,
        bottom=0.34 + row * 0.19,
    )
    for row in range(4)
    for column in range(2)
)


class InvalidWorksheetImage(ValueError):
    pass


def normalize_image(image_bytes: bytes, max_edge: int = 1800) -> Image.Image:
    if not image_bytes:
        raise InvalidWorksheetImage("empty image")
    Image.MAX_IMAGE_PIXELS = get_settings().max_image_pixels
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_bytes)) as opened:
                opened.verify()
            with Image.open(BytesIO(image_bytes)) as opened:
                image = ImageOps.exif_transpose(opened).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise InvalidWorksheetImage("The upload is not a safe, readable PNG or JPEG image") from exc
    width, height = image.size
    if width < 320 or height < 320:
        raise InvalidWorksheetImage("The worksheet image is too small to segment reliably")
    if max(image.size) > max_edge:
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    return image


def crop_normalized_image(
    image: Image.Image,
    regions: Iterable[TemplateRegion] = FRACTIONS_V1,
) -> list[WorksheetCrop]:
    width, height = image.size
    output: list[WorksheetCrop] = []
    for region in regions:
        if not (0 <= region.left < region.right <= 1 and 0 <= region.top < region.bottom <= 1):
            raise InvalidWorksheetImage(f"invalid template region: {region.id}")
        box = (
            max(0, round(region.left * width)),
            max(0, round(region.top * height)),
            min(width, round(region.right * width)),
            min(height, round(region.bottom * height)),
        )
        if box[2] <= box[0] or box[3] <= box[1]:
            raise InvalidWorksheetImage(f"invalid template region: {region.id}")
        cropped = image.crop(box)
        buffer = BytesIO()
        cropped.save(buffer, format="PNG", optimize=True)
        output.append(WorksheetCrop(region.id, buffer.getvalue(), cropped.width, cropped.height))
    if not output:
        raise InvalidWorksheetImage("The template contains no worksheet regions")
    return output


def crop_template(
    image_bytes: bytes,
    regions: Iterable[TemplateRegion] = FRACTIONS_V1,
) -> list[WorksheetCrop]:
    return crop_normalized_image(normalize_image(image_bytes), regions)
