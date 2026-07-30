from pathlib import Path


def test_api_source_does_not_log_uploaded_content() -> None:
    root = Path(__file__).resolve().parents[1] / "faultline_api"
    source = "\n".join(path.read_text() for path in root.rglob("*.py"))
    forbidden = ["print(content)", "logger.info(content)", "logger.debug(content)"]
    assert not any(token in source for token in forbidden)
