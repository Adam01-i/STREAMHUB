from app.services.ads.base import AdProvider


class NullAdProvider(AdProvider):
    """Provider par défaut : n'affiche jamais de publicité. Utilisé quand AD_PROVIDER=none
    ou quand la configuration d'un vrai provider est incomplète."""

    def is_enabled(self) -> bool:
        return False

    def render(self, placement: str) -> str | None:
        return None


class GoogleAdSenseProvider(AdProvider):
    def __init__(self, client_id: str, slot_ids: dict[str, str]) -> None:
        self.client_id = client_id
        self.slot_ids = slot_ids

    def is_enabled(self) -> bool:
        return bool(self.client_id)

    def render(self, placement: str) -> str | None:
        slot_id = self.slot_ids.get(placement)
        if not slot_id:
            return None
        return (
            f'<ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{self.client_id}" data-ad-slot="{slot_id}" '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f"<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>"
        )
