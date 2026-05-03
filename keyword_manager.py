"""
keyword_manager.py — Loads and queries the keyword set from keywords.txt.
Keeping keywords data-driven (not hardcoded) as required.
"""

from pathlib import Path


class KeywordManager:
    """Loads keywords from a text file and answers membership queries."""

    def __init__(self, filepath: str | Path | None = None):
        if filepath is None:
            filepath = Path(__file__).parent / "keywords.txt"
        self._keywords: set[str] = self._load(Path(filepath))

    # ------------------------------------------------------------------
    @staticmethod
    def _load(path: Path) -> set[str]:
        if not path.exists():
            raise FileNotFoundError(f"Keyword file not found: {path}")
        keywords: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.strip()
            if word and not word.startswith("#"):
                keywords.add(word)
        return keywords

    # ------------------------------------------------------------------
    def is_keyword(self, word: str) -> bool:
        return word in self._keywords

    def all_keywords(self) -> frozenset[str]:
        return frozenset(self._keywords)
