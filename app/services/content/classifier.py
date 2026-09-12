import enum


class ContentType(str, enum.Enum):
    FOOTBALL = "football"
    MOVIE = "movie"
    SERIES = "series"
    NEWS = "news"
    UNKNOWN = "unknown"


_FOOTBALL_KEYWORDS = [
    "football", "soccer", "match", "liga", "ligue 1", "ligue des champions",
    "champions league", "premier league", "la liga", "serie a", "bundesliga",
    "coupe du monde", "world cup", "afcon", "can ", "uefa", "fifa", " vs ", " v ", "derby",
]
_MOVIE_KEYWORDS = ["film", "movie", "cinéma", "cinema", "long métrage"]
_SERIES_KEYWORDS = ["série", "series", "saison", "season", "épisode", "episode", "s01", "ep."]
_NEWS_KEYWORDS = ["journal", "news", "actualité", "info", "flash info", "édition"]

_SCORE_THRESHOLD = 1  # exige au moins un vrai signal ; sinon UNKNOWN, jamais deviné

# Catégories iptv-org utilisées comme repli d'exploration lorsque l'EPG ne fournit aucun programme.
# Ce mapping ne prétend JAMAIS qu'un contenu précis est diffusé : il sert uniquement à orienter
# vers les chaînes thématiques concernées.
FALLBACK_CATEGORY_BY_CONTENT_TYPE: dict[ContentType, str] = {
    ContentType.FOOTBALL: "sports",
    ContentType.MOVIE: "movies",
    ContentType.SERIES: "series",
    ContentType.NEWS: "news",
}


def _score_text(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def classify_program_text(
    title: str, description: str | None = None, category: str | None = None
) -> tuple[ContentType, int]:
    """Classifie un programme EPG réel à partir de son titre/description/catégorie.
    Retourne (type, score). UNKNOWN si aucun signal n'atteint le seuil — jamais de classification
    par défaut arbitraire.
    """
    combined = " ".join(filter(None, [title, description or "", category or ""]))

    scores: dict[ContentType, int] = {
        ContentType.FOOTBALL: _score_text(combined, _FOOTBALL_KEYWORDS),
        ContentType.MOVIE: _score_text(combined, _MOVIE_KEYWORDS),
        ContentType.SERIES: _score_text(combined, _SERIES_KEYWORDS),
        ContentType.NEWS: _score_text(combined, _NEWS_KEYWORDS),
    }

    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score < _SCORE_THRESHOLD:
        return ContentType.UNKNOWN, 0
    return best_type, best_score
