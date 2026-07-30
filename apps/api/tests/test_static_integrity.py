from html.parser import HTMLParser
from pathlib import Path


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        key = "src" if tag == "script" else "href" if tag == "link" else None
        value = values.get(key, "") if key else ""
        if value.startswith("assets/") or value.startswith("/assets/"):
            self.references.append(value)


def test_all_local_page_assets_exist() -> None:
    static = Path(__file__).resolve().parents[2] / "web-static"
    for page in (static / "index.html", static / "judge.html"):
        parser = AssetParser()
        parser.feed(page.read_text(encoding="utf-8"))
        assert parser.references
        for reference in parser.references:
            relative = reference.removeprefix("/")
            assert (static / relative).exists(), reference
