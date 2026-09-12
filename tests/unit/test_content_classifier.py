from app.services.content.classifier import ContentType, classify_program_text


def test_classifies_football_match() -> None:
    content_type, score = classify_program_text("Barcelona vs Real Madrid", "Liga - Journée 10")
    assert content_type == ContentType.FOOTBALL
    assert score >= 1


def test_classifies_movie() -> None:
    content_type, _ = classify_program_text("Film du soir : The Equalizer")
    assert content_type == ContentType.MOVIE


def test_classifies_series() -> None:
    content_type, _ = classify_program_text("Série - Saison 3 Épisode 4")
    assert content_type == ContentType.SERIES


def test_unknown_when_no_signal() -> None:
    content_type, score = classify_program_text("Programme du soir")
    assert content_type == ContentType.UNKNOWN
    assert score == 0


def test_never_classifies_football_from_category_alone() -> None:
    # Un titre neutre avec juste la catégorie "Sports" ne doit PAS être classé football
    # sans signal explicite dans le titre/description (règle anti-invention).
    content_type, _ = classify_program_text("Émission du soir", category="Sports")
    assert content_type == ContentType.UNKNOWN
