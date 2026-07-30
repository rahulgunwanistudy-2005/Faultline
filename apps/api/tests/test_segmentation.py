from io import BytesIO

from PIL import Image

from faultline_api.services.segmentation import FRACTIONS_V1, crop_template, normalize_image


def image_bytes(width: int = 1200, height: int = 1600) -> bytes:
    image = Image.new("RGB", (width, height), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_normalization_limits_large_edge() -> None:
    image = normalize_image(image_bytes(2400, 3200), max_edge=1200)
    assert max(image.size) <= 1200


def test_fixed_template_returns_eight_nonempty_crops() -> None:
    crops = crop_template(image_bytes())
    assert len(crops) == len(FRACTIONS_V1) == 8
    assert [crop.region_id for crop in crops] == [f"p{i}" for i in range(1, 9)]
    assert all(crop.width > 0 and crop.height > 0 and crop.image_bytes for crop in crops)
